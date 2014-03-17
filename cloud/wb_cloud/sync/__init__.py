import logging
from datetime import datetime

import pytz
from sqlalchemy.orm.exc import NoResultFound

from wb_cloud.models import Instance, User, Image, InstanceType

logger = logging.getLogger(__name__)

class CloudSyncManager(object):
    def __init__(self, cloud, model, db_session, ldap_client):
        """
        cloud is an instance of weatherballoon.cloudconnection
        model is an instance of weatherballoon.models.Cloud
        session is a scoped sqlalchemy session
        """
        self.cloud = cloud
        self.model = model
        self.db_session = db_session
        self.ldap_client = ldap_client
        
    def get_monitored_vms(self):
        """
        return a list of weatherballoon.models.Instance in a cloud that
        are currently being monitored
        """
        return self.db_session.query(Instance)\
            .filter(Instance.end_date == None)\
            .filter(Instance.cloud == self.model)

    def get_user_model(self, user_id):
        """
        Get a user model from the cloud. Match it to a database record if possible.
        Else, look the user up in ldap. If that doesn't work, just save the user
        anyway.
        """
        cloud_user = self.cloud.get_user(user_id)
        try:
            user = self.db_session.query(User).filter(User.username == cloud_user.name).one()
        except NoResultFound:
            ldapuser = self.ldap_client.get_user(cloud_user.name)
            staff_users = self.ldap_client.get_staff_users()
            if ldapuser is not None:
                user = User(
                    username=cloud_user.name,
                    name=ldapuser['cn'][0],
                    mail=ldapuser['mail'][0],
                    is_staff=cloud_user.name in staff_users
                )
            else:
                user = User(
                    username=cloud_user.name
                )
            self.db_session.add(user)
        return user


    def get_image_model(self, image_id):
        """
        given a cloud and an image_id (emi-4d5F6CC), grab the corresponding image from the
        database.  If it doesn't exist, create it.
        """
        try:
            model = self.db_session.query(Image)\
                .filter(Image.cloud == self.model)\
                .filter(Image.image_id == image_id).one()
        except NoResultFound:
            image = self.cloud.get_image(image_id)
            model = Image(
                cloud=self.model,
                image_id=image.id,
                type=image.type
            )
            self.db_session.add(model)
        return model

    def get_instance_type_model(self, type_id):
        """
        given a cloud and a type_alias like 'm1.small', grab the corresponding InstanceType
        model
        """
        type = self.cloud.get_instance_type(type_id)
        try:
            type = self.db_session.query(InstanceType).filter(InstanceType.cloud == self.model)\
                .filter(InstanceType.name == type.name).one()
        except NoResultFound:
            type = InstanceType(
                cloud=self.model,
                name=type.name
            )
            self.db_session.add(type)
        return type

    def create_instance_model(self, instance):
        """
        given instances of a weatherballoon.cloud.CloudConnection, a 
        weatherballoon.models.Cloud and a weatherballon.cloud.models.Instance,
        save a new instance of weatherballoon.models.Instance
        """
        type = self.get_instance_type_model(instance.instance_type_id)
        image = self.get_image_model(instance.image_id)
        user = self.get_user_model(instance.user_id)

        logger.debug(instance.__dict__)
        i = Instance(
            instance_id=instance.id,
            user=user,
            address=str(instance.ip_address),
            #start_date=datetime.utcnow().replace(tzinfo=pytz.utc),
            created_date=instance.launch_time,
            type=type,
            cloud=self.model,
            image=image,
            client_name="%s_%s" % (self.model.name, instance.id)
        )
        logger.debug(i.__dict__)
        self.db_session.add(i)
        return i
    
    def end_vms(self, instances):
        """
        given a list a weatherballoon.models.Instance, end date them all
        """
        ids = [instance.id for instance in instances]
        now = datetime.utcnow().replace(tzinfo=pytz.utc)
        self.db_session.query(Instance)\
            .filter(Instance.id.in_(ids))\
            .update({'end_date': now}, synchronize_session='fetch')

    def synchronize(self):
        """
        Synchronizes the database state with the cloud. Returns the list of
        instances that require deployment of the monitoring client
        """
        monitored_vms = self.get_monitored_vms()
        monitored_ids = set(vm.instance_id for vm in monitored_vms)

        try:
            instances = self.cloud.get_running_instances()
        except:
            raise Exception("Bad response for cloud %s" % self.model.name)

        active_ids = set(i.id for i in instances)

        terminated_ids = monitored_ids - active_ids
        new_ids = active_ids - monitored_ids

        terminated_vms = [vm for vm in monitored_vms if vm.instance_id in terminated_ids]
        self.end_vms(terminated_vms)

        new_vms = [i for i in instances if i.id in new_ids]
        logger.debug('new_vms:')
        logger.debug(new_vms)

        to_deploy = []

        for instance in new_vms:
            model = self.create_instance_model(instance)
            self.db_session.commit()
            to_deploy.append(model)

        for instance in monitored_vms:
            if instance.start_date == None:
                to_deploy.append(instance)

        logger.debug("\tmonitored vms:" + str(monitored_ids))
        logger.debug("\tactive_vms: " + str(active_ids))
        logger.debug("\tterminated_ids: " + str(terminated_ids))
        logger.debug("\tnew_ids: " + str(new_ids))

        return to_deploy
