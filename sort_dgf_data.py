import jsonlines
import os

accept_classifications_code = [1409, 240403, 2415, 14080, 160, 6202010, 6202020, 6202025, 10]

reject_classifications_code = [8, 11702, 9]

accept_codes_if_eurovoc = [160, 115010, 1701, 1710]

eurovoc_unacceptable = ["state aid", "control of state aid", "tax law", "tax evasion", "tax avoidance", "tax system",
                        "tax on investment income", "corporation tax", "indirect tax", "tax relief", "fuel tax"]

eurovoc_acceptable = ["accounting", "bank charges", "banking policy", "capital market", "capital transfer",
                      "capital increase", "consumer credit", "counterfeiting", "credit institution", "credit guarantee",
                      "electronic banking", "European Central Bank", "Euribor", "financial aid", "financial control",
                      "financial instrument", "financial institution", "financial intervention",
                      "financial legislation", "financial market", "financial provisions", "financial stability",
                      "financial services ", "financial solvency", "financial transaction", "shareholding",
                      "share capital", "insurance", "insurance company ", "insurance contract", "investment company",
                      "investment protection", "market supervision ", "money laundering", "private-sector liquidity",
                      "pension scheme", "regulation of investments", "transparency", "securities", "stock exchange"]

def check_eurovoc(line):
    if not line['eurovoc']:
        return negative
    if line['eurovoc']:
        n = 0
        for x in line['eurovoc']:
            if x in eurovoc_acceptable:
                n += 1
        if n > 1 and not any(x in eurovoc_unacceptable for x in line['eurovoc']):
            return positive


accepted = []
rejected = []
odir = '/nas/frederic/dg-fisma/export-eurlex/data'
for fileName in os.listdir(odir):
    with jsonlines.open(os.path.join(odir, fileName), 'r') as rf:
        for line in rf:
            try:
                if 'Financial Services and Capital Markets Union' in line['misc_author']:
                    # print(str(os.path.join(odir, fileName)))
                    accepted.append(fileName)
                    continue
                if 'FISMA' in line['misc_department_responsible']:
                    # print(str(os.path.join(odir, fileName)))
                    accepted.append(fileName)
                    continue
                for code in line['classifications_code']:
                    if code in accept_classifications_code:
                        accepted.append(fileName)
                        continue
                    if code in reject_classifications_code:
                        rejected.append(fileName)
                        continue
                    if code in accept_codes_if_eurovoc:
                        result = check_eurovoc(line)
                        if result == positive:
                            accepted.append(fileName)
                            continue
                        if result == negative:
                            rejected.append(fileName)
            except:
                continue