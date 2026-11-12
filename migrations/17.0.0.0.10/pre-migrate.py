"""v0.0.10: pin the two accounts that a seeded journal uses as its default account.

See hooks.py (``pin_journal_default_accounts``) for the full reasoning. In short:
data/account.account.csv re-writes ``account_type`` on every upgrade, and for

    account_account_creditors_control_trade  (22010010, liability_payable)  <- journal CP
    account_account_sales_advances           (22020170, liability_payable)  <- journal ADVR

that write is rejected, because each is the ``default_account_id`` of a journal
and account's ``_check_account_is_bank_journal_bank_account`` forbids a journal
default account being receivable or payable:

    You cannot change the type of an account set as Bank Account on a journal
    to Receivable or Payable.

The pairing loads on a fresh install purely because the account is created
before the journal exists, so flag the two rows noupdate and let the data load
skip them. The remaining 765 seeded accounts are re-imported as before.

This runs for databases installed before the flag existed; post_init_hook covers
new installs. Kept self-contained on purpose -- a pre-migration runs before the
module is importable, so it does not import hooks.py.
"""

import logging

_logger = logging.getLogger(__name__)

MODULE = "Jinasena_MasterData_Accounting"
PINNED_ACCOUNTS = (
    "account_account_creditors_control_trade",
    "account_account_sales_advances",
)


def migrate(cr, version):
    if not version:
        return

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
