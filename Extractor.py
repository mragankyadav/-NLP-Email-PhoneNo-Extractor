import sys
import os
import re
import pprint



def process_file(name, f):
    #Regex for Email Search
    email1_start = '(\w+)\s*'
    email1_mid='(?:@|\s+at\s+|&#x40\.|\(at\))'
    email1_end='\s*([a-zA-Z0-9\.]+)\s*\.\s*(edu|com|co\...)'
    email_normal_pattern=email1_start+email1_mid+email1_end
    email_hidden_pattern = "obfuscate\('([a-zA-Z0-9\.]+)','([a-zA-Z0-9\.]+)'\)"
    
    #Regex for Mobile Search
    phone_start='\(?(\d{3})\s*(?:\)|\s|'
    phone_mid='-|&thinsp;)\s*(\d{3})\s*(?:\s|'
    phone_end='-|&thinsp;)\s*(\d{4})'
    phone=phone_start+phone_mid+phone_end
    
    returnValue = []
    for line in f:
        numbers = re.findall(phone, line)
        for n in numbers:
            number = '%s-%s-%s' % n
            returnValue.append((name,'p',number))
            
        #Preprocessing on every line.
        line = line.replace('-','')
        line = re.sub(r'\s*([\s+\(]dom[\s+\)]|[\s+\(]dot[\s+\)]|;)\s*', '.', line, 1000, re.IGNORECASE)
        line = re.sub(r'\s*([\s+\(]where[\s+\)])\s*', '@', line, 1000, re.IGNORECASE)
        
        #Finding the text pattern.
        matched = re.findall(email_normal_pattern, line, re.IGNORECASE)
        for match in matched:
            if match[0].lower() != 'server':
                email = '%s@%s.%s' % match
                returnValue.append((name,'e',email))
        matched = re.findall(email_hidden_pattern, line, re.IGNORECASE)
        for match in matched:
            email = '%s@%s' % (match[1],match[0])
            returnValue.append((name,'e',email))
            
    return returnValue

"""
You should not need to edit this function, nor should you alter
its interface
"""
def process_dir(data_path):
    # get candidates
    guess_list = []
    for fname in os.listdir(data_path):
        if fname[0] == '.':
            continue
        path = os.path.join(data_path,fname)
        f = open(path,'r')
        f_guesses = process_file(fname, f)
        guess_list.extend(f_guesses)
    return guess_list

"""
You should not need to edit this function.
Given a path to a tsv file of gold e-mails and phone numbers
this function returns a list of tuples of the canonical form:
(filename, type, value)
"""
def get_gold(gold_path):
    # get gold answers
    gold_list = []
    f_gold = open(gold_path,'r')
    for line in f_gold:
        gold_list.append(tuple(line.strip().split('\t')))
    return gold_list

"""
You should not need to edit this function.
Given a list of guessed contacts and gold contacts, this function
computes the intersection and set differences, to compute the true
positives, false positives and false negatives.  Importantly, it
converts all of the values to lower case before comparing
"""
def score(guess_list, gold_list):
    guess_list = [(fname, _type, value.lower()) for (fname, _type, value) in guess_list]
    gold_list = [(fname, _type, value.lower()) for (fname, _type, value) in gold_list]
    guess_set = set(guess_list)
    gold_set = set(gold_list)

    tp = guess_set.intersection(gold_set)
    fp = guess_set - gold_set
    fn = gold_set - guess_set

    pp = pprint.PrettyPrinter()
    #print 'Guesses (%d): ' % len(guess_set)
    #pp.pprint(guess_set)
    #print 'Gold (%d): ' % len(gold_set)
    #pp.pprint(gold_set)
    print 'True Positives (%d): ' % len(tp)
    pp.pprint(tp)
    print 'False Positives (%d): ' % len(fp)
    pp.pprint(fp)
    print 'False Negatives (%d): ' % len(fn)
    pp.pprint(fn)
    print 'Summary: tp=%d, fp=%d, fn=%d' % (len(tp),len(fp),len(fn))

"""
You should not need to edit this function.
It takes in the string path to the data directory and the
gold file
"""
def main(data_path, gold_path):
    guess_list = process_dir(data_path)
    gold_list =  get_gold(gold_path)
    score(guess_list, gold_list)

"""
commandline interface takes a directory name and gold file.
It then processes each file within that directory and extracts any
matching e-mails or phone numbers and compares them to the gold file
"""
if __name__ == '__main__':
    if (len(sys.argv) != 3):
        print 'usage:\tSpamLord.py <data_dir> <gold_file>'
        sys.exit(0)
    main(sys.argv[1],sys.argv[2])
