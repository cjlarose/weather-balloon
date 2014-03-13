import ldap

class LDAPClient():
    
    def __init__(self, server):
        self.server = server
        self.l = ldap.initialize(self.server)

    def get_users(self):
        results = self.l.search_s('ou=People,dc=iplantcollaborative,dc=org', ldap.SCOPE_SUBTREE)    
        users = []
        for dn, entry in results:
            users.append(entry)
        return users

    def get_user(self, uid):
        results = self.l.search_s('ou=People,dc=iplantcollaborative,dc=org', ldap.SCOPE_SUBTREE, '(uid=%s)' % (uid))
        if len(results) > 0:
            (dn, entry) = results[0]
            return entry
        else:
            return None

    def get_group_members(self, group_name):
        results = self.l.search_s('ou=Groups,dc=iplantcollaborative,dc=org', ldap.SCOPE_SUBTREE, '(cn=%s)' % group_name)
        (dn, entry) = results[0]
        return entry['memberUid']

    def get_staff_users(self):
        return self.get_group_members('staff')

    def get_core_services_users(self):
        return self.get_group_members('core-services')
