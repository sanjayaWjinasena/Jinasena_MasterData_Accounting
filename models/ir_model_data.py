# -*- coding: utf-8 -*-
"""Bind our xmlids to records that already exist on the target DB.

Called from data/00_bind_xmlids.xml BEFORE the CSVs it guards. For each CSV row whose xmlid
is not registered yet, look for an existing record with the same natural key
(e.g. an account with the same code in the same company, created by the chart
of accounts) and register our xmlid on it, so the CSV load updates that record
instead of inserting a duplicate. Same approach as Jinasena_MasterData_Stock.
"""
import csv
import logging
import os
from odoo import api, models

_logger = logging.getLogger(__name__)

MODULE = 'Jinasena_MasterData_Accounting'
# (group, model, csv file under data/, [(db field, csv column), ...][, {csv column: required value}])
BINDS = [
    ('accounts', 'account.tax.group', 'account.tax.group.csv', [('name', 'name'), ('company_id', 'company_id/id')]),
    ('accounts', 'account.account', 'account.account.csv', [('code', 'code'), ('company_id', 'company_id/id')]),
    ('accounts', 'account.account', 'account.account.csv', [('account_type', 'account_type'), ('company_id', 'company_id/id')], {'account_type': 'equity_unaffected'}),
    ('accounts', 'account.tax', 'account.tax.csv', [('name', 'name'), ('type_tax_use', 'type_tax_use'), ('company_id', 'company_id/id')]),
    ('accounts', 'account.journal', 'account.journal.csv', [('code', 'code'), ('company_id', 'company_id/id')]),
]


class IrModelData(models.Model):
    _inherit = 'ir.model.data'

    @api.model
    def _jinasena_md_accounting_bind(self, group=None):
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        for g, model, rel, match_fields, *only in BINDS:
            if group is None or g == group:
                self._jinasena_md_bind_one(MODULE, model, os.path.join(data_dir, rel), match_fields, only[0] if only else None)
        return True

    @api.model
    def _jinasena_md_bind_one(self, module, model, csv_path, match_fields, only=None):
        if not os.path.exists(csv_path) or model not in self.env:
            return
        IMD = self.sudo()
        Model = self.env[model].sudo().with_context(active_test=False)
        bound = 0
        with open(csv_path, encoding='utf-8', newline='') as f:
            rows = list(csv.DictReader(f))
        for row in rows:
            xmlid = row.get('id')
            if not xmlid or IMD.search_count([('module', '=', module), ('name', '=', xmlid)]):
                continue
            if only and any(row.get(k, '') != v for k, v in only.items()):
                continue
            domain = []
            for db_field, col in match_fields:
                val = row.get(col, '')
                if col.endswith('/id'):
                    rec = self.env.ref(val, raise_if_not_found=False) if val else None
                    if val and not rec:
                        domain = None
                        break
                    domain.append((db_field, '=', rec.id if rec else False))
                else:
                    if not val:
                        domain = None
                        break
                    domain.append((db_field, '=', val))
            if not domain:
                continue
            rec = Model.search(domain, limit=1)
            if rec and not IMD.search_count([('model', '=', model), ('res_id', '=', rec.id), ('module', '=', module)]):
                IMD.create({'module': module, 'name': xmlid, 'model': model, 'res_id': rec.id, 'noupdate': False})
                bound += 1
        _logger.info('[%s] bound %s existing %s rows', module, bound, model)
