# -*- coding: utf-8 -*-
"""Pin the two accounts whose account_type cannot be rewritten once their journal exists.

data/account.account.csv seeds 767 accounts. Two of them are also the
``default_account_id`` of a journal seeded by data/account.journal.csv:

    account_account_creditors_control_trade  (22010010)  <- journal CP
    account_account_sales_advances           (22020170)  <- journal ADVR

Both are ``liability_payable``, and account's ``_check_account_is_bank_journal_bank_account``
rejects an account that is a journal's default account being receivable or
payable. The pairing survives a fresh install only because of ordering: the
account is created first, with no journal pointing at it yet, and the constraint
is declared ``@api.constrains('account_type')`` -- creating the journal
afterwards never re-checks it.

A re-import is a different matter. It writes account_type again (with the same
value -- Odoo validates the field because it was written, not because it
changed), the journal now exists, and the load dies:

    You cannot change the type of an account set as Bank Account on a journal
    to Receivable or Payable.

So these two rows are one-shot by construction, and are flagged noupdate:
``_load_records`` skips a noupdate xmlid in update mode, so their account_type
is never rewritten. The other 765 accounts keep being re-seeded as before --
this is deliberately not a switch that turns the seeding off.

Whether journals CP and ADVR should point at a payable control account at all is
a question for the chart of accounts, not for the loader; pinning keeps the
database exactly as Clear-DB has it until that is decided.
"""

import logging

_logger = logging.getLogger(__name__)

MODULE = "Jinasena_MasterData_Accounting"

# Accounts that are a seeded journal's default_account_id and are receivable/payable.
PINNED_ACCOUNTS = (
    "account_account_creditors_control_trade",
    "account_account_sales_advances",
)


def pin_journal_default_accounts(cr):
    """Flag the conflicting account.account rows noupdate. Safe to re-run."""
    cr.execute(
        """
        UPDATE ir_model_data
           SET noupdate = true
         WHERE module = %s
           AND model = 'account.account'
           AND name IN %s
           AND noupdate IS NOT TRUE
     RETURNING name
        """,
        (MODULE, PINNED_ACCOUNTS),
    )
    pinned = [r[0] for r in cr.fetchall()]
    if pinned:
        _logger.info(
            "Pinned %s account(s) as noupdate (journal default account, receivable/payable): %s",
            len(pinned),
            ", ".join(pinned),
        )
    return pinned


def post_init_hook(env):
    pin_journal_default_accounts(env.cr)
