import json
import os
import sys
import requests
import zipfile
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin, urlparse
import asyncio
import aiohttp
import aiofiles
import shutil

# Load configuration from JSON file
CONFIG_PATH = os.getenv("CONFIG_PATH", "config.json")

try:
    # Try to load config from the specified path
    config_file = Path(CONFIG_PATH)
    if not config_file.is_absolute():
        # If relative path, make it relative to the directory containing this script
        script_dir = Path(__file__).parent
        config_file = script_dir / config_file
    
    if not config_file.exists():
        print(f"Config file not found: {config_file}", file=sys.stderr)
        raise FileNotFoundError(f"Config file not found: {config_file}")
    
    with open(config_file, 'r') as cfg_file:
        config = json.load(cfg_file)
except Exception as e:
    print(f"Error loading config from {CONFIG_PATH}: {e}", file=sys.stderr)
    # Fallback to default config
    config = {
        "base_url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
        "email": "flothomatthias@gmail.com",
        "api_key": "",
        "retmax": 20,
        "download_dir": "./downloads",
        "max_file_size_mb": 500,
        "max_total_downloads_mb": 2000,
        "max_concurrent_downloads": 3,
        "download_timeout_seconds": 300,
        "allowed_download_paths": ["./downloads", "/tmp/geo_downloads"]
    }
    print("Using default configuration", file=sys.stderr)

# Configuration
BASE_URL = config.get("base_url", "https://eutils.ncbi.nlm.nih.gov/entrez/eutils")
EMAIL = config.get("email", "flothomatthias@gmail.com")
API_KEY = config.get("api_key", "")
DOWNLOAD_DIR = config.get("download_dir", "./downloads")
MAX_FILE_SIZE_MB = config.get("max_file_size_mb", 500)
MAX_TOTAL_DOWNLOADS_MB = config.get("max_total_downloads_mb", 2000)
MAX_CONCURRENT_DOWNLOADS = config.get("max_concurrent_downloads", 3)
DOWNLOAD_TIMEOUT_SECONDS = config.get("download_timeout_seconds", 300)
ALLOWED_DOWNLOAD_PATHS = config.get("allowed_download_paths", ["./downloads", "/tmp/geo_downloads"])

# Convert MB to bytes
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MAX_TOTAL_DOWNLOADS_BYTES = MAX_TOTAL_DOWNLOADS_MB * 1024 * 1024

# Ensure download directory exists and is allowed
download_path = Path(DOWNLOAD_DIR)
if not download_path.is_absolute():
    download_path = Path(__file__).parent / download_path

# Validate download path is allowed
def _is_path_allowed(path: Path) -> bool:
    """Check if a path is in the allowed download paths."""
    path = path.resolve()
    for allowed_path in ALLOWED_DOWNLOAD_PATHS:
        allowed = Path(allowed_path)
        if not allowed.is_absolute():
            allowed = Path(__file__).parent / allowed
        allowed = allowed.resolve()
        if path == allowed or path.is_relative_to(allowed):
            return True
    return False

if not _is_path_allowed(download_path):
    raise ValueError(f"Download path {download_path} is not in allowed paths: {ALLOWED_DOWNLOAD_PATHS}")

download_path.mkdir(parents=True, exist_ok=True)

# Semaphore for limiting concurrent downloads
download_semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)


def _get_directory_size(path: Path) -> int:
    """Calculate total size of a directory in bytes."""
    total_size = 0
    try:
        for file_path in path.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
    except Exception:
        pass
    return total_size


def _check_disk_space(path: Path, required_size: int) -> bool:
    """Check if there's enough disk space available."""
    try:
        stat = shutil.disk_usage(path)
        return stat.free >= required_size
    except Exception:
        return False


def _validate_output_path(output_path: Path) -> bool:
    """Validate that the output path is safe and allowed."""
    try:
        output_path = output_path.resolve()
        return _is_path_allowed(output_path)
    except Exception:
        return False


def _efetch(db: str, id: str, rettype: str = "xml", retmode: str = "text") -> str:
    """Fetch data from NCBI E-Utils using EFetch."""
    params = {
        'db': db,
        'id': id,
        'rettype': rettype,
        'retmode': retmode,
        'email': EMAIL,
    }
    if API_KEY:
        params['api_key'] = API_KEY
    
    resp = requests.get(f"{BASE_URL}/efetch.fcgi", params=params)
    resp.raise_for_status()
    return resp.text


def _get_geo_download_urls(geo_id: str, db_type: str) -> List[str]:
    """Get download URLs for a GEO dataset/series/sample."""
    # Different GEO databases have different download patterns
    if db_type == "gds":
        # GEO DataSets - download from GEO website
        return [f"https://www.ncbi.nlm.nih.gov/geo/download/?acc={geo_id}&format=file&file={geo_id}.soft.gz"]
    elif db_type == "gse":
        # GEO Series - download from GEO website
        return [f"https://www.ncbi.nlm.nih.gov/geo/download/?acc={geo_id}&format=file&file={geo_id}_family.soft.gz"]
    elif db_type == "gsm":
        # GEO Samples - download from GEO website
        return [f"https://www.ncbi.nlm.nih.gov/geo/download/?acc={geo_id}&format=file&file={geo_id}.soft.gz"]
    elif db_type == "gpl":
        # GEO Platforms - download from GEO website
        return [f"https://www.ncbi.nlm.nih.gov/geo/download/?acc={geo_id}&format=file&file={geo_id}.soft.gz"]
    else:
        return []


async def download_geo_data(geo_id: str, db_type: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
    """Download GEO data for a given ID and database type with size and path validation."""
    async with download_semaphore:  # Limit concurrent downloads
        if output_dir is None:
            output_dir = str(download_path / db_type / geo_id)
        
        output_path = Path(output_dir)
        
        # Validate output path
        if not _validate_output_path(output_path):
            raise ValueError(f"Output path {output_path} is not allowed. Allowed paths: {ALLOWED_DOWNLOAD_PATHS}")
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Check current download directory size
        current_size = _get_directory_size(download_path)
        if current_size >= MAX_TOTAL_DOWNLOADS_BYTES:
            raise ValueError(f"Total download size limit exceeded. Current: {current_size / (1024*1024):.1f}MB, Max: {MAX_TOTAL_DOWNLOADS_MB}MB")
        
        # Get download URLs
        download_urls = _get_geo_download_urls(geo_id, db_type)
        
        if not download_urls:
            raise ValueError(f"No download URLs available for {db_type}:{geo_id}")
        
        downloaded_files = []
        total_downloaded_size = 0
        
        timeout = aiohttp.ClientTimeout(total=DOWNLOAD_TIMEOUT_SECONDS)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for url in download_urls:
                try:
                    filename = url.split('/')[-1]
                    file_path = output_path / filename
                    
                    # Check if we have enough disk space (estimate 2x file size for extraction)
                    estimated_size = MAX_FILE_SIZE_BYTES * 2
                    if not _check_disk_space(output_path, estimated_size):
                        raise ValueError(f"Insufficient disk space for download")
                    
                    # Download file with size limit
                    async with session.get(url) as response:
                        if response.status == 200:
                            # Check content length if available
                            content_length = response.headers.get('content-length')
                            if content_length:
                                file_size = int(content_length)
                                if file_size > MAX_FILE_SIZE_BYTES:
                                    raise ValueError(f"File size {file_size / (1024*1024):.1f}MB exceeds limit of {MAX_FILE_SIZE_MB}MB")
                            
                            # Download with size monitoring
                            downloaded_size = 0
                            async with aiofiles.open(file_path, 'wb') as f:
                                async for chunk in response.content.iter_chunked(8192):
                                    if downloaded_size + len(chunk) > MAX_FILE_SIZE_BYTES:
                                        raise ValueError(f"File size limit exceeded during download")
                                    
                                    await f.write(chunk)
                                    downloaded_size += len(chunk)
                                    
                                    # Check total downloads size
                                    if total_downloaded_size + downloaded_size > MAX_TOTAL_DOWNLOADS_BYTES:
                                        raise ValueError(f"Total download size limit exceeded")
                            
                            downloaded_files.append(str(file_path))
                            total_downloaded_size += downloaded_size
                            
                            # If it's a gzipped file, extract it
                            if filename.endswith('.gz'):
                                import gzip
                                
                                extracted_path = file_path.with_suffix('')
                                
                                # Check extracted file size before extracting
                                with gzip.open(file_path, 'rb') as f_in:
                                    # Read first few bytes to estimate size
                                    f_in.seek(0, 2)  # Seek to end
                                    compressed_size = f_in.tell()
                                    f_in.seek(0)
                                    
                                    # Rough estimate: compressed size * 3 for text files
                                    estimated_extracted_size = compressed_size * 3
                                    if estimated_extracted_size > MAX_FILE_SIZE_BYTES:
                                        raise ValueError(f"Estimated extracted file size {estimated_extracted_size / (1024*1024):.1f}MB exceeds limit")
                                
                                with gzip.open(file_path, 'rb') as f_in:
                                    with open(extracted_path, 'wb') as f_out:
                                        shutil.copyfileobj(f_in, f_out)
                                
                                downloaded_files.append(str(extracted_path))
                        else:
                            print(f"Failed to download {url}: {response.status}", file=sys.stderr)
                            
                except Exception as e:
                    print(f"Error downloading {url}: {e}", file=sys.stderr)
                    # Clean up partial downloads
                    if 'file_path' in locals() and file_path.exists():
                        file_path.unlink()
                    raise
        
        # Also fetch metadata using EFetch
        try:
            metadata = _efetch(db_type, geo_id, rettype="xml", retmode="text")
            metadata_file = output_path / f"{geo_id}_metadata.xml"
            with open(metadata_file, 'w') as f:
                f.write(metadata)
            downloaded_files.append(str(metadata_file))
        except Exception as e:
            print(f"Error fetching metadata: {e}", file=sys.stderr)
        
        return {
            "geo_id": geo_id,
            "db_type": db_type,
            "output_dir": str(output_path),
            "downloaded_files": downloaded_files,
            "total_size_mb": total_downloaded_size / (1024 * 1024),
            "status": "completed" if downloaded_files else "failed"
        }


async def download_geo_batch(geo_ids: List[str], db_type: str, output_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    """Download multiple GEO datasets in batch with size monitoring."""
    results = []
    
    for geo_id in geo_ids:
        try:
            result = await download_geo_data(geo_id, db_type, output_dir)
            results.append(result)
        except Exception as e:
            results.append({
                "geo_id": geo_id,
                "db_type": db_type,
                "error": str(e),
                "status": "failed"
            })
    
    return results


def get_download_status(geo_id: str, db_type: str) -> Dict[str, Any]:
    """Check if a GEO dataset has been downloaded."""
    expected_dir = download_path / db_type / geo_id
    
    if not expected_dir.exists():
        return {
            "geo_id": geo_id,
            "db_type": db_type,
            "downloaded": False,
            "status": "not_downloaded"
        }
    
    files = list(expected_dir.glob("*"))
    total_size = sum(f.stat().st_size for f in files if f.is_file())
    
    return {
        "geo_id": geo_id,
        "db_type": db_type,
        "downloaded": True,
        "status": "downloaded",
        "files": [str(f) for f in files],
        "file_count": len(files),
        "total_size_mb": total_size / (1024 * 1024)
    }


def list_downloaded_datasets(db_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all downloaded datasets."""
    results = []
    
    if db_type:
        db_path = download_path / db_type
        if db_path.exists():
            for geo_dir in db_path.iterdir():
                if geo_dir.is_dir():
                    results.append(get_download_status(geo_dir.name, db_type))
    else:
        # List all database types
        for db_dir in download_path.iterdir():
            if db_dir.is_dir():
                for geo_dir in db_dir.iterdir():
                    if geo_dir.is_dir():
                        results.append(get_download_status(geo_dir.name, db_dir.name))
    
    return results


def get_download_stats() -> Dict[str, Any]:
    """Get overall download statistics."""
    total_size = _get_directory_size(download_path)
    total_files = sum(1 for f in download_path.rglob('*') if f.is_file())
    
    return {
        "total_downloads_mb": total_size / (1024 * 1024),
        "max_allowed_mb": MAX_TOTAL_DOWNLOADS_MB,
        "total_files": total_files,
        "download_path": str(download_path),
        "max_file_size_mb": MAX_FILE_SIZE_MB,
        "max_concurrent_downloads": MAX_CONCURRENT_DOWNLOADS
    }


def cleanup_downloads(geo_id: Optional[str] = None, db_type: Optional[str] = None) -> Dict[str, Any]:
    """Clean up downloaded files."""
    if geo_id and db_type:
        # Remove specific dataset
        target_path = download_path / db_type / geo_id
        if target_path.exists():
            shutil.rmtree(target_path)
            return {
                "action": "cleanup",
                "target": f"{db_type}:{geo_id}",
                "status": "removed"
            }
        else:
            return {
                "action": "cleanup",
                "target": f"{db_type}:{geo_id}",
                "status": "not_found"
            }
    elif db_type:
        # Remove all datasets of a specific type
        target_path = download_path / db_type
        if target_path.exists():
            shutil.rmtree(target_path)
            return {
                "action": "cleanup",
                "target": db_type,
                "status": "removed"
            }
        else:
            return {
                "action": "cleanup",
                "target": db_type,
                "status": "not_found"
            }
    else:
        # Remove all downloads
        if download_path.exists():
            shutil.rmtree(download_path)
            download_path.mkdir(parents=True, exist_ok=True)
            return {
                "action": "cleanup",
                "target": "all",
                "status": "removed"
            } 