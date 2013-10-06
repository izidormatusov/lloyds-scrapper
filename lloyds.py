import mechanize
import re


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
        return self._agent.response().read()


if __name__ == "__main__":
    bank = LloydsBank()
    bank.login('id', 'password', 'secret')
    for account_url in bank.accounts:
        print bank.get_transactions(account_url)
