class MockImageSaver:
    def __init__(self):
        self.saved_images = []

    def save(self, image_bytes, name_hint=None):
        self.saved_images.append({"bytes": len(image_bytes), "hint": name_hint})
        return f"/mock/path/{name_hint or 'image'}"