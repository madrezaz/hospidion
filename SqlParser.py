class SqlParser:
    def __init__(self,query):
        self.query = query
        self.type = None
        self.target = None
        self.table = None
        self.conitions = None
        self.values = None
        self.col = None
    
    def parse(self):
        pieces = self.query.split()
        if pieces[0].lower() == 'select':
            self.type = 'select'
            self.target = pieces[1]
            self.table = pieces[3]
            self.conitions = pieces[5]
        elif pieces[0].lower() == 'insert':
            self.type = 'insert'
            self.table = pieces[2]
            self.values = pieces[4]
        elif pieces[0].lower() == 'update':
            self.type = 'update'
            self.table = pieces[1]
            self.col = pieces[3]
            self.values = pieces[5]
            self.conitions = pieces[7]
        elif pieces[0].lower() == 'delete':
            self.type = 'delete'
            self.table = pieces[2]
            self.conitions = pieces[5]
        else:
            print("Unknown command!")
    
    def addDionConditions(self):
        #additional information needed: username,write or rea
        pass

    def __str__(self):
        #return manipulated query
        pass

