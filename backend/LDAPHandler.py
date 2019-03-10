from helpers.Config import Config
from helpers.Tools import Tools
from ldap3 import Connection, Server, ALL, SUBTREE
import getpass

LDAPAuthType = {
    "LOGIN": 0x001f,
    "ANONYMOUS": 0x002f   
}

class LDAPHandler:
    def __init__(self):
        self.__config = self.__getLDAPConfig()
        self.__connection = False
        self.__currentUser = False
    
    def __requestAnonymousConnection(self, ldapConfig):
        conn = Connection(
            server=Server(
                host=ldapConfig["server"], 
                port=ldapConfig["port"], 
                use_ssl=False, 
                get_info='NO_INFO',
            ),
            authentication="ANONYMOUS",
            version=ldapConfig["version"]
        )
        try:
            conn.bind()
            return conn
        except:
            return False

    def __requestLoginConnection(self, ldapConfig):
        ldap_bind_dn = "CN="+ldapConfig["username"]+",OU="+ldapConfig["organizational_unit"]+",O="+ldapConfig["organization"]
        conn = Connection(
            server=Server(
                host=ldapConfig["server"], 
                port=ldapConfig["port"], 
                use_ssl=False, 
                get_info='NO_INFO'
            ),
            user=ldap_bind_dn,
            password=ldapConfig["password"],
            authentication="SIMPLE",
            version=ldapConfig["version"]
        )
        try:
            conn.bind()
            return conn
        except:
            return False

    def __getLDAPConfig(self):
        ldapConfig = {}
        ldapConfig["server"] = Tools.getValue(Config.get("/LDAP/server", True), "localhost")
        ldapConfig["port"] = Tools.getValue(int(Config.get("/LDAP/port", True)), 389)
        ldapConfig["organizational_unit"] = Config.get("/LDAP/organizational_unit", True)
        ldapConfig["organization"] = Config.get("/LDAP/organization", True)
        ldapConfig["version"] = Tools.getValue(Config.get("/LDAP/version", True), 3)

        ldapConfig["username"] = Config.get("/LDAP/credentials/username", True)
        ldapConfig["password"] = Config.get("/LDAP/credentials/password", True)
        ldapConfig["authType"] = LDAPAuthType["ANONYMOUS"]
        if ldapConfig["username"] != False and ldapConfig["password"] != False:
            ldapConfig["authType"] = LDAPAuthType["LOGIN"]
        return ldapConfig

    def __requestConnection(self):
        ldapConfig = self.__config
        authType = ldapConfig["authType"]
        if(authType == LDAPAuthType["ANONYMOUS"]):
            return self.__requestAnonymousConnection(ldapConfig)
        if(authType == LDAPAuthType["LOGIN"]):
            return self.__requestLoginConnection(ldapConfig)
        return False

    def __getUser(self, username):
        if self.__connection and self.__config:
            organization = self.__config["organization"]
            organizational_unit = self.__config["organizational_unit"]
            searchBase = "CN="+username+",OU="+organizational_unit+",O="+organization
            self.__connection.search(
                search_base=searchBase,
                search_filter="(objectClass=*)",
                attributes=["cn", "givenName", "mail", "accountBalance", "sn"]
            )
            response = self.__connection.response
            if(len(response) > 0):
                return response[0]["attributes"]
        return False

    def useUser(self, userId):
        currentUser = self.__getUser(userId)
        if(currentUser):
            self.__currentUser = currentUser
            return True
        else:
            return False

    def releaseUser(self):
        self.__currentUser = False
        return True

    def getPoints(self):
        if self.__currentUser:
            accountBalance = self.__currentUser["accountBalance"]
            if(len(accountBalance) > 0):
                return accountBalance[0] 
        return False

    def getFirstname(self):
        if self.__currentUser:
            givenName = self.__currentUser["givenName"]
            if(len(givenName) > 0):
                return givenName[0]
        return False

    def getLastname(self):
        if self.__currentUser:
            sn = self.__currentUser["sn"]
            if(len(sn) > 0):
                return sn[0]
        return False
    
    def getEmail(self):
        if self.__currentUser:
            email = self.__currentUser["mail"]
            if(len(email) > 0):
                return email[0]
        return False

    def setPoints(self, points):
        if self.__connection and self.__config and self.__currentUser:
            organization = self.__config["organization"]
            organizational_unit = self.__config["organizational_unit"]
            searchBase = "CN="+self.__currentUser["cn"][0]+",OU="+organizational_unit+",O="+organization

            try:
                changes = {}
                changes["accountBalance"] = str(points)
                self.__connection.modify(searchBase, changes)
                return True
            except:
                return False
        return False

    def getExchangeRate(self, euros):
        return Tools.getValue(Config.get("/LDAP/exchangeRate", True), 250) * euros

    def releaseConnection(self):
        self.__connection.unbind()

    def connect(self):
        self.__connection = self.__requestConnection()