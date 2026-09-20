# -*- coding: utf-8 -*-
{
    'name': 'Jinasena : MasterData : Accounting',
    'version': '17.0.0.0.2',
    'summary': 'Master-data extracted from CDB for Accounting domain.',
    'description': 'Extracted from Clear-DB. Test-env master data. Edit the CSVs in data/ to add/remove rows before install.',
    'author': 'Jinasena Agricultural Machinery (Pvt) Ltd.',
    'category': 'Extra Tools',
    'license': 'LGPL-3',
    'depends': [
        'BugFix-Accounting',
        'Jinasena_MasterData_Common',
    ],
    'data': [
        'data/account.payment.term.csv',
        'data/account.analytic.plan.csv',
        'data/account.analytic.account.csv',
        'data/x_journal_types.csv',
        'data/x_custom_currency.csv',
        'data/x_custom_currency_rate.csv',
        'data/link/x_customer_group.csv',
        'data/link/x_vendor_group.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
