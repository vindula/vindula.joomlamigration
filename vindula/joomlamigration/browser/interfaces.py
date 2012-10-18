# -*- coding: utf-8 -*-
from zope.interface import Interface

class IMigration(Interface):

	def importData():
		"""
		Traz objetos do contexto
		"""
	def getListaConteudo():
		"""
		...
		"""
	def getConteudo():
		"""
		...
		"""
	def fixLinks():
		"""
		Conserta os links que usam UID.
		"""
	def ImportAll():
	    """
	    Importa todo conteudo de um container.
	    """
	def fixModificationDate():
	    """
	    Corrige Datas.
	    """