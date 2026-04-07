"""ImageDeduplicator: near-duplicate detection using perceptual hashing (pHash)."""

import logging
from io import BytesIO

try:
    import imagehash
    from PIL import Image
except ImportError:
    raise RuntimeError(
        "imagehash not installed -- run: pip install imagehash Pillow"
    )

logger = logging.getLogger(__name__)


class ImageDeduplicator:
    """Detects near-duplicate images using perceptual hashing (pHash).

    Stores hashes in memory for the current run. Hamming distance below
    the threshold indicates a near-duplicate.
    """

    def __init__(self, threshold: int = 10):
        self.threshold = threshold
        self._hashes: dict[str, imagehash.ImageHash] = {}

    def compute_phash(self, image_data: bytes) -> imagehash.ImageHash | None:
        """Compute pHash for image bytes. Returns None if image is corrupt."""
        try:
            img = Image.open(BytesIO(image_data))
            return imagehash.phash(img)
        except Exception as e:
            logger.warning("Failed to compute pHash: %s", e)
            return None

    def is_duplicate(
        self, source_url: str, image_data: bytes
    ) -> tuple[bool, str | None]:
        """Check if an image is a near-duplicate of any stored image.

        Returns (is_duplicate, reason_string_or_None).
        """
        phash = self.compute_phash(image_data)
        if phash is None:
            return False, None  # let downstream decide

        for existing_url, existing_hash in self._hashes.items():
            distance = phash - existing_hash
            if distance < self.threshold:
                reason = (
                    f"Near-duplicate of {existing_url} "
                    f"(Hamming distance: {distance}, threshold: {self.threshold})"
                )
                logger.warning("Rejected duplicate: %s", reason)
                return True, reason

        # Not a duplicate — store the hash
        self._hashes[source_url] = phash
        return False, None

    def add_existing_hash(self, source_url: str, phash_hex: str) -> None:
        """Add a pre-computed hash (from DB) to the dedup store."""
        self._hashes[source_url] = imagehash.hex_to_hash(phash_hex)

    def get_hash_hex(self, source_url: str) -> str | None:
        """Return the hex string of the stored hash for a source_url."""
        h = self._hashes.get(source_url)
        return str(h) if h is not None else None

    @property
    def count(self) -> int:
        """Number of unique hashes stored."""
        return len(self._hashes)
