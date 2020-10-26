import re

BEGIN_TOKEN = 'BEGIN:VCARD'
END_TOKEN = 'END:VCARD'
FN_TOKEN = 'FN:'
LN_TOKEN = 'LN:'
ADR_TOKEN = 'ADR;'
EMAIL_TOKEN = 'EMAIL;'

ADDRESS_REGEX = re.compile(r'ADR;TYPE=(?P<type>\w+).*:(?P<line_1>[^;]*);(?P<line_2>[^;]*);(?P<street_line>[^;]*);(?P<city>[^;]*);(?P<state>[^;]*);(?P<zipcode>[^;]*);(?P<country>.*)')
EMAIL_REGEX = re.compile(r'EMAIL;TYPE=(?P<type>\w+).*:(?P<email>.*)')

def line_producer(fh):

    cur_line = None
    for line in fh:
        line = line.rstrip()
        if not line.startswith(' '):

            if cur_line is not None:
                yield cur_line

            cur_line = line

        elif cur_line is None:
            raise Exception('invalid format - expected a tag, got a space')
        else:
            cur_line += line.strip()

    # process the last line
    yield cur_line

def read_card(line_producer):
    """
    Create a dictionary for a card that has just started... stop reading
    when an END:VCARD is hit.
    """
    vcf_card = {'addresses': {}, 'email_addresses': {}}

    for line in line_producer:

        if line.startswith(END_TOKEN):
            return vcf_card

        # this shouldn't happen
        if len(line) == 0:
            continue

        # skip binary stuff
        if line.startswith('PHOTO'):
            continue

        # get name
        if line.startswith(FN_TOKEN):
            vcf_card['first_name'] = line[len(FN_TOKEN):]

        if line.startswith(LN_TOKEN):
            vcf_card['last_name'] = line[len(LN_TOKEN):]

        # get addresses
        if line.startswith(ADR_TOKEN):
            match = ADDRESS_REGEX.match(line) 

            if match is None:
                print(f'Error parsing address line: {line}')
            else:
                vcf_card['addresses'][match.group('type')] = {
                    'street_line': match.group('street_line'),
                    'city': match.group('city'),
                    'state': match.group('state'),
                    'zipcode': match.group('zipcode'),
                    'country': match.group('country')
                }

        # get emails
        if line.startswith(EMAIL_TOKEN):
            match = EMAIL_REGEX.match(line)

            if match is None:
                print(f'Error parsing email line: {line}')
            else:
                vcf_card['email_addresses'][match.group('type')] = match.group('email')
        
    raise Exception('Expected a card end token, got EOF')

class Reader:

    def __init__(self, filename):
        self.filename = filename

    def __iter__(self):
        fh = open(self.filename, 'r')
        lp = line_producer(fh)

        for line in lp:
            if line.startswith('BEGIN:VCARD'):
                yield read_card(lp)
