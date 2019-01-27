Routes = [
    { 'path' : "/", 'handler' : 'home_get', 'methods': ['GET'] }, 
    { 'path' : "/users", 'handler' : 'user_post', 'methods': ['POST'] }, 
    { 'path' : "/tests", 'handler' : 'test_get', 'methods': ['GET'] }, 
    { 'path' : "/tests/<id>", 'handler' : 'test_get', 'methods': ['GET'] }, 
    { 'path' : "/tests", 'handler' : 'test_post', 'methods': ['POST'] }, 
]