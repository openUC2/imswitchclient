class communicationManager(object):
    
    def __init__(self, parent):
        self.parent = parent
        
    def acquireImage(self):
        """Acquire an image through the communication channel"""
        url = f"{self.parent.base_uri}/CommunicationChannel/acquireImage"
        headers = {'accept': 'application/json'}
        response = self.parent.get_json(url, headers=headers)
        return response
    
    def getImage(self):
        """Get an image from the communication channel"""
        url = f"{self.parent.base_uri}/CommunicationChannel/get_image"
        headers = {'accept': 'application/json'}
        response = self.parent.get_json(url, headers=headers)
        return response