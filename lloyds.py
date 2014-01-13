import csv
import mechanize
import re
from decimal import Decimal as D
from datetime import date, datetime

class Transaction(object):
    """ Single transaction """

    EXPLANATIONS = {
        'BGC': 'Bank giro credit',
        'BP': 'Bill payment',
        'CD': 'Card payment * (followed by the last 4 digits of the card)',
        'CHG': 'Charge',
        'CHQ': 'Cheque',
        'COMM': 'Commission',
        'COR': 'Correction',
        'CPT': 'Cashpoint',
        'CSH': 'Cash',
        'CSQ': 'Cash / Cheque',
        'DD': 'Direct Debit',
        'DEB': 'Debit card',
        'DEP': 'Deposit',
        'DR': 'Overdrawn balance',
        'EUR': 'Euro cheque',
        'FPI': 'Faster payments incoming',
        'FPO': 'Faster payments outgoing',
        'IB': 'Internet Banking',
        'MTU': 'Mobile top up',
        'PAY': 'Payment',
        'PSV': 'Paysave',
        'SAL': 'Salary',
        'SO': 'Standing order',
        'TFR': 'Transfer',
    }

    def __init__(self, fields):
        dt = datetime.strptime(fields['Transaction Date'], '%d/%m/%Y')
        self.date = date(dt.year, dt.month, dt.day)

        self.transaction_type = fields['Transaction Type']

        self.account_number = fields['Account Number']
        self.sort_code = fields['Sort Code'].strip("'")

        if fields['Debit Amount']:
            self.amount = -D(fields['Debit Amount'])
        else:
            self.amount = D(fields['Credit Amount'])

        self.balance = D(fields['Balance'])
        self.card = None

        self.raw_description = fields['Transaction Description']
        self.description = self._parse_description()

    def _parse_description(self):
        """ Parse the cryptic description:
            - remove date from end
            - remove card detail
        """
        desc = self.raw_description.strip()
        end_date = self.date.strftime("%d%b%y").upper()
        if desc.endswith(end_date):
            desc = desc[:-len(end_date)].strip()
        match = re.match('(.*?) CD (\d{4})$', desc)
        if match:
            desc = match.group(1).strip()
            self.card = match.group(2)
        return desc

    def __str__(self):
        return "Transaction(%s, %s, %s, %s)" % (
            self.date.strftime('%d/%m/%Y'), self.get_type_explanation(),
            self.description, self.amount)

    def get_type_explanation(self):
        """ Return explanation of type """
        if self.transaction_type.startswith('CD'):
            four_digits = self.transaction_type[len('CD '):]
            return 'Paid by card **** **** **** %d' % four_digits
        else:
            return self.EXPLANATIONS.get(self.transaction_type, '')


class LloydsBank(object):

    USER_AGENT = 'Mozilla/5.0 Gecko/20100101 Firefox/24.0'
    LOGIN_URL = 'https://online.lloydsbank.co.uk/personal/logon/login.jsp'

    def __init__(self):
        self._agent = mechanize.Browser()
        # Ignore robots, they prevent everybody
        self._agent.set_handle_robots(False)
        self._agent.addheaders = [('User-agent', self.USER_AGENT)]
        self.accounts = [] 

    def login(self, user_id, password, secret):
        """ Log into internet account """
        # Login credentials
        self._agent.open(self.LOGIN_URL)
        self._agent.select_form('frmLogin')
        self._agent['frmLogin:strCustomerLogin_userID'] = user_id
        self._agent['frmLogin:strCustomerLogin_pwd'] = password
        self._agent.submit()

        # Secret information
        form_name = 'frmentermemorableinformation1'
        self._agent.select_form(form_name)
        prefix = '%s:strEnterMemorableInformation_memInfo' % form_name
        for control in self._agent.form.controls:
            if control.name.startswith(prefix):
                label = control.get_labels()[0].text
                position = int(re.findall(r'^Character (\d+) :$', label)[0])
                # Make position to be 0-indexed
                position -= 1
                assert 0 <= position < len(secret)
                self._agent[control.name] = ["&nbsp;" + secret[position]]
        self._agent.submit()

        assert 'Personal Account Overview' in self._agent.title()

        # Save list of accounts
        self.accounts = []
        for link in self._agent.links():
            attrs = dict(link.attrs)
            if 'lkImageRetail' in attrs.get('id', ''):
                self.accounts.append(link.absolute_url)

    def get_transactions(self, account_url):
        self._agent.open(account_url)
        export_link = self._agent.find_link(text="Export")
        self._agent.follow_link(export_link)
        self._agent.select_form('frmTest')
        self._agent.submit()

        rows = csv.DictReader(self._agent.response())
        return [Transaction(row) for row in rows]
