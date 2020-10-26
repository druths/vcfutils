from arghandler import subcmd, ArgumentHandler
from .reader import Reader

@subcmd
def export_csv(parser, context, args):
    parser.add_argument('-e','--emails_required',action='store_true',help='only export contacts with emails')
    parser.add_argument('vcf_file')
    parser.add_argument('csv_file')

    args = parser.parse_args(args)

    reader = Reader(args.vcf_file)

    fh = open(args.csv_file, 'w')

    fh.write('first_name,last_name,email_address\n')

    for vcf in reader:

        if args.emails_required and len(vcf['email_addresses']) == 0:
            continue

        fh.write(f'{vcf.get("first_name","")},{vcf.get("last_name","")},{",".join(vcf["email_addresses"].values())}')
        fh.write('\n')


def main():
    parser = ArgumentHandler()

    parser.run()


if __name__ == '__main__':
    main()
