from pathlib import Path
import json
from .document.document import Document
from secsgml import parse_sgml_content_into_memory
from secsgml.utils import bytes_to_str, calculate_documents_locations_in_tar
from secsgml.parse_sgml import transform_metadata_string
import tarfile
import shutil
import zstandard as zstd
import gzip
import io



def write_submission_to_tar(output_path,metadata,documents,standardize_metadata,compression_list):
     # Write tar directly to disk
    with tarfile.open(output_path, 'w') as tar:

        # calculate document locations in tar
        metadata = calculate_documents_locations_in_tar(metadata, documents)
        
        # serialize metadata
        metadata_str  = bytes_to_str(metadata,lower=False)
        metadata_json = json.dumps(metadata_str).encode('utf-8')
        # save metadata
        tarinfo = tarfile.TarInfo(name='metadata.json')
        tarinfo.size = len(metadata_json)
        tar.addfile(tarinfo, io.BytesIO(metadata_json))

        for file_num, content in enumerate(documents, 0):
            if standardize_metadata:
                document_name = metadata['documents'][file_num]['filename'] if metadata['documents'][file_num].get('filename') else metadata['documents'][file_num]['sequence'] + '.txt'
            
            compression = compression_list[file_num]
            if compression == 'gzip':
                document_name = f'{document_name}.gz'
            elif compression == 'zstd':
                document_name = f'{document_name}.zst'

           
            tarinfo = tarfile.TarInfo(name=f'{document_name}')
            tarinfo.size = len(content)
            tar.addfile(tarinfo, io.BytesIO(content))

class Submission:
    def __init__(self, path=None, sgml_content=None, keep_document_types=None,
                 batch_tar_path=None, accession_prefix=None, portfolio_ref=None):
        
        # Validate parameters
        param_count = sum(x is not None for x in [path, sgml_content, batch_tar_path])
        if param_count != 1:
            raise ValueError("Exactly one of path, sgml_content, or batch_tar_path must be provided")
        
        if batch_tar_path is not None and (accession_prefix is None or portfolio_ref is None):
            raise ValueError("batch_tar_path requires both accession_prefix and portfolio_ref")
        
        # Initialize batch tar attributes
        self.batch_tar_path = batch_tar_path
        self.accession_prefix = accession_prefix
        self.portfolio_ref = portfolio_ref
        
        if sgml_content is not None:
            self.path = None
            metadata, raw_documents = parse_sgml_content_into_memory(sgml_content)

            # standardize metadata
            metadata = transform_metadata_string(metadata)

            self.metadata = Document(type='submission_metadata', content=metadata, extension='.json',filing_date=None,accession=None,path=None)
            # code dupe
            self.accession = self.metadata.content['accession-number']
            self.filing_date= f"{self.metadata.content['filing-date'][:4]}-{self.metadata.content['filing-date'][4:6]}-{self.metadata.content['filing-date'][6:8]}"
    
            self.documents = []
            filtered_metadata_documents = []

            for idx,doc in enumerate(self.metadata.content['documents']):
                type = doc.get('type')
                
                # Keep only specified types
                if keep_document_types is not None and type not in keep_document_types:
                    continue

                # write as txt if not declared
                filename = doc.get('filename','.txt')
                extension = Path(filename).suffix
                self.documents.append(Document(type=type, content=raw_documents[idx], extension=extension,filing_date=self.filing_date,accession=self.accession))

                filtered_metadata_documents.append(doc)
            
            self.metadata.content['documents'] = filtered_metadata_documents

        elif batch_tar_path is not None:
            # Batch tar case
            self.path = None
            
            # Load metadata from batch tar
            with self.portfolio_ref.batch_tar_locks[batch_tar_path]:
                tar_handle = self.portfolio_ref.batch_tar_handles[batch_tar_path]
                metadata_obj = tar_handle.extractfile(f'{accession_prefix}/metadata.json')
                metadata = json.loads(metadata_obj.read().decode('utf-8'))

            # Set metadata path using :: notation
            metadata_path = f"{batch_tar_path}::{accession_prefix}/metadata.json"
            
            # standardize metadata
            metadata = transform_metadata_string(metadata)
            self.metadata = Document(type='submission_metadata', content=metadata, extension='.json',filing_date=None,accession=None,path=metadata_path)
            self.accession = self.metadata.content['accession-number']
            self.filing_date= f"{self.metadata.content['filing-date'][:4]}-{self.metadata.content['filing-date'][4:6]}-{self.metadata.content['filing-date'][6:8]}"

        elif path is not None:
            self.path = Path(path)  
            if self.path.suffix == '.tar':
                with tarfile.open(self.path,'r') as tar:
                    metadata_obj = tar.extractfile('metadata.json')
                    metadata = json.loads(metadata_obj.read().decode('utf-8'))

                # tarpath
                metadata_path = f"{self.path}::metadata.json"
            else:
                metadata_path = self.path / 'metadata.json'
                with metadata_path.open('r') as f:
                    metadata = json.load(f) 

            # standardize metadata
            metadata = transform_metadata_string(metadata)
            self.metadata = Document(type='submission_metadata', content=metadata, extension='.json',filing_date=None,accession=None,path=metadata_path)
            self.accession = self.metadata.content['accession-number']
            self.filing_date= f"{self.metadata.content['filing-date'][:4]}-{self.metadata.content['filing-date'][4:6]}-{self.metadata.content['filing-date'][6:8]}"
    


    def compress(self, compression=None, level=None, threshold=1048576):
        if self.path is None:
            raise ValueError("Compress requires path")
        
        if compression is not None and compression not in ['gzip', 'zstd']:
            raise ValueError("compression must be 'gzip' or 'zstd'")
        
        # check if we're loading from a dir or a tar file
        is_dir_not_tar = True
        if self.path.suffix == '.tar':
            is_dir_not_tar = False
        elif not self.path.is_dir():
            raise ValueError("Path must be a directory to compress")
        # Create tar file (replace directory with .tar file)
        tar_path = self.path.with_suffix('.tar')

        # load all files in the directory or tar file
        documents = [doc.content.encode('utf-8') if isinstance(doc.content, str) else doc.content for doc in self]
        

        # we should compress everything here first.
        compression_list = [compression if len(doc) >= threshold else '' for doc in documents]
        documents = [gzip.compress(doc, compresslevel=level or 6) if compression == 'gzip' and 
            len(doc) >= threshold else zstd.ZstdCompressor(level=level or 3).compress(doc) if compression == 'zstd' and 
            len(doc) >= threshold else doc for doc in documents]
        
        metadata = self.metadata.content.copy()
        write_submission_to_tar(tar_path,metadata,documents,compression_list=compression_list,standardize_metadata=True)

        # Delete original folder
        if is_dir_not_tar:
            shutil.rmtree(self.path)
            # otherwise, we already replaced the tar file
            # Update path to point to new tar file
            self.path = tar_path

    def decompress(self):
        if self.path is None:
            raise ValueError("Decompress requires path")
        elif self.path.suffix != '.tar':
            raise ValueError("Can only decompress tar")
        
        # Create output directory (path without .tar extension)
        output_dir = self.path.with_suffix('')
        output_dir.mkdir(exist_ok=True)
        
        with tarfile.open(self.path, 'r') as tar:
            for member in tar.getmembers():
                if member.isfile():
                    content = tar.extractfile(member).read()
                    
                    # Decompress based on file extension
                    if member.name.endswith('.gz'):
                        content = gzip.decompress(content)
                        output_path = output_dir / member.name[:-3]  # Remove .gz extension
                    elif member.name.endswith('.zst'):
                        dctx = zstd.ZstdDecompressor()
                        content = dctx.decompress(content)
                        output_path = output_dir / member.name[:-4]  # Remove .zst extension
                    else:
                        output_path = output_dir / member.name
                    
                    # check if it is metadata.json
                    if output_path.name == 'metadata.json':
                        # load as json
                        metadata = json.loads(content.decode('utf-8'))
                        # remove SECSGML_START_BYTE and SECSGML_END_BYTE from documents
                        for doc in metadata['documents']:
                            if 'secsgml_start_byte' in doc:
                                del doc['secsgml_start_byte']
                            
                            if 'secsgml_end_byte' in doc:
                                del doc['secsgml_end_byte']

                        with output_path.open('w', encoding='utf-8') as f:
                            json.dump(metadata, f)
                    else:
                        # Write to output directory
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        with output_path.open('wb') as f:
                            f.write(content)

        # delete original file
        self.path.unlink()
        self.path = output_dir

    def _load_document_by_index(self, idx):
        """Load a document by its index in the metadata documents list."""
        doc = self.metadata.content['documents'][idx]
        
        # If loaded from sgml_content, return pre-loaded document
        if self.path is None and self.batch_tar_path is None:
            return self.documents[idx]
        
        # Get filename
        filename = doc.get('filename')
        if filename is None:
            filename = doc['sequence'] + '.txt'

        extension = Path(filename).suffix

        # Handle batch tar case
        if self.batch_tar_path is not None:
            with self.portfolio_ref.batch_tar_locks[self.batch_tar_path]:
                tar_handle = self.portfolio_ref.batch_tar_handles[self.batch_tar_path]
                
                # Try different filename variations for compressed files
                possible_filenames = [
                    f'{self.accession_prefix}/{filename}',
                    f'{self.accession_prefix}/{filename}.gz',
                    f'{self.accession_prefix}/{filename}.zst'
                ]
                
                content = None
                actual_filename = None
                for attempt_filename in possible_filenames:
                    try:
                        content = tar_handle.extractfile(attempt_filename).read()
                        actual_filename = attempt_filename
                        break
                    except:
                        continue
                
                if content is None:
                    raise ValueError(f"Could not find document in batch tar: {self.batch_tar_path}, accession: {self.accession_prefix}, filename: {filename}")
                
                # Decompress if compressed
                if actual_filename.endswith('.gz'):
                    content = gzip.decompress(content)
                elif actual_filename.endswith('.zst'):
                    dctx = zstd.ZstdDecompressor()
                    content = dctx.decompress(content)
                
                # Decode text files
                if extension in ['.htm', '.html', '.txt', '.xml']:
                    content = content.decode('utf-8', errors='replace')
                
                document_path = f"{self.batch_tar_path}::{self.accession_prefix}/{filename}"
        
        # Handle regular path case (existing logic)
        else:
            document_path = self.path / filename

            if self.path.suffix == '.tar':
                with tarfile.open(self.path, 'r') as tar:
                    # so here is where we should use bytes instead with byte offset.
                    # bandaid fix TODO
                    try:
                        content = tar.extractfile(filename).read()
                    except:
                        try:
                            content = tar.extractfile(filename+'.gz').read()
                        except:
                            try: 
                                content = tar.extractfile(filename+'.zst').read()
                            except:
                                # some of these issues are on SEC data end, will fix when I setup cloud.
                                raise ValueError(f"Something went wrong with tar: {self.path}")
                    # Decompress if compressed
                    if filename.endswith('.gz'):
                        content = gzip.decompress(content)
                    elif filename.endswith('.zst'):
                        dctx = zstd.ZstdDecompressor()
                        content = dctx.decompress(content)
            else:
                with document_path.open('rb') as f:
                    content = f.read()

                # Decode text files
                if extension in ['.htm', '.html', '.txt', '.xml']:
                    content = content.decode('utf-8', errors='replace')

        return Document(
            type=doc['type'], 
            content=content, 
            extension=extension,
            filing_date=self.filing_date,
            accession=self.accession,
            path=document_path
        )

    def __iter__(self):
        """Make Submission iterable by yielding all documents."""
        for idx in range(len(self.metadata.content['documents'])):
            yield self._load_document_by_index(idx)

    def document_type(self, document_type):
        """Yield documents matching the specified type(s)."""
        # Convert single document type to list for consistent handling
        if isinstance(document_type, str):
            document_types = [document_type]
        else:
            document_types = [item for item in document_type]

        for idx, doc in enumerate(self.metadata.content['documents']):
            if doc['type'] in document_types:
                yield self._load_document_by_index(idx)