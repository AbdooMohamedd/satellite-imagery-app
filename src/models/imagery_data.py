class ImageryData:
    def __init__(self, image_url, timestamp, metadata, section_id=None, local_path=None, image_data=None):
        self.image_url = image_url
        self.timestamp = timestamp
        self.metadata = metadata
        self.section_id = section_id  # ID of the section this image belongs to
        self.local_path = local_path  # Path where the image is saved locally
        self.image_data = image_data  # Binary image data (if available)
    
    def __repr__(self):
        return f"ImageryData(image_url={self.image_url}, timestamp={self.timestamp}, section_id={self.section_id})"
    
    def to_dict(self):
        """Convert the object to a dictionary"""
        result = {
            "image_url": self.image_url,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "section_id": self.section_id,
            "local_path": self.local_path
        }
        
        # Only include image_data if it exists and is requested
        if hasattr(self, 'image_data') and self.image_data is not None:
            result["has_image_data"] = True
        
        return result
    
    @classmethod
    def from_dict(cls, data_dict):
        """Create an instance from a dictionary"""
        return cls(
            image_url=data_dict["image_url"],
            timestamp=data_dict["timestamp"],
            metadata=data_dict["metadata"],
            section_id=data_dict.get("section_id"),
            local_path=data_dict.get("local_path")
        )