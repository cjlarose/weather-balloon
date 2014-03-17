class CloudConnection(object):
    def get_running_instances(self):
        """
        return a list of all instances as models.Instance
        """
        raise NotImplementedError()

    def get_image(self, image_id):
        """
        given an image_id, return corresponding models.Image
        """
        raise NotImplementedError()

    def get_user(self, user_id):
        """
        given a user_id, return corresponding models.User
        """
        raise NotImplementedError()

    def get_instance_type(self, type_id):
        raise NotImplementedError()
