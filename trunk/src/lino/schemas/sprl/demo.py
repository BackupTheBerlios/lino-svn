# coding: latin1
"""
"""


import os
#from lino.adamo import quickdb, Application
from lino import adamo
#from lino.misc.console import Console
from sprl import Schema



def populate(sess,big=False):
	from lino.schemas.sprl.data import std,demo1
	std.populate(sess,big)
	demo1.populate(sess,big)


		
def beginSession(populator=populate,
					  langs=None,
					  isTemporary=True,
					  verbose=False,
					  **kw):
	schema = Schema(**kw)
	return adamo.beginQuickSession(schema,
											 populator=populate,
											 langs=None,
											 isTemporary=True,
											 verbose=False)

# old name:
getDemoDB = beginSession

if __name__ == '__main__':
	sess = beginSession()
	#db.installto(globals())
	for partner in sess.context.tables.PARTNERS.query(orderBy="name"):
		print partner
	sess.shutdown()
