import os

def whereAmI():

    host = os.environ.get('HOSTNAME')
    imperial = "ic.ac.uk"
    cern = "cern.ch"
    if not host: return "I have no idea where I am"
    
    if imperial in host and cern in host:
        print "Ambiguous hostname"
        return "Ambiguous hostname"
    elif imperial in host:
        return "Imperial"
    elif cern in host:
        return "CERN"
    else:
        print "I have no idea where I am"
        return "I have no idea where I am"

if __name__ == '__main__':
    print whereAmI()
