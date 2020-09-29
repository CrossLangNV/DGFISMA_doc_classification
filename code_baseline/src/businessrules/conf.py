'''
Directory codes:

ACCEPTED
062020  = Right of establishment and freedom to provide services / Sectoral application
160     = General, financial and institutional matters / Financial and budgetary provisions
1040    = Economic and monetary policy and free movement of capital / Free movement of capital
1030    = Economic and monetary policy and free movement of capital / Economic policy

REJECTED
08      = Competition policy
09      = Taxation
117020  = External relations / Development policy / Aid to developing countries

Eurovoc descriptors:

ACCEPTED
4838    = European Investment Bank
5455    = European Central Bank
5460	= European Bank for Reconstruction and Development
5465    = Money laundering
8434    = Counterfeiting

REJECTED
889     = State aid

Subject matter:

ACCEPTED
BEI     = European Investment Bank
BCE     = European Central Bank

REJECTED

Summary codes:

ACCEPTED
1409    = Economic and monetary affairs / Banking and financial services
2414    = Internal market / Banking and finance
240403  = Internal market / Single market for services / Financial services: insurance

REJECTED

'''

accepted_classifications = {
    'directory code': ['062020', '0160', '1040', '1030'],
    'eurovoc descriptor': ['4838', '5455', '5460', '5465', '8434'],
    'subject matter': ['BEI', 'BCE'],
    'summary codes': ['1409', '2414', '240403']
}

rejected_classifications = {
    'directory code': ['08', '117020', '09'],
    'eurovoc descriptor': ['889'],
    'subject matter': [],
    'summary codes': []
}
accepted_authors = ['Directorate-General for Financial Stability, Financial Services and Capital Markets Union']
rejected_authors = []

accepted_departments = []
rejected_departments = []