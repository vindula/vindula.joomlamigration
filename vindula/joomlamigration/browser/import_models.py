# -*- coding: utf-8 -*-
from storm.locals import *
from storm.locals import Store
from zope.component import getUtility
from storm.zope.interfaces import IZStorm
from datetime import datetime

db_string = "mysql://root:vindula@localhost:3306/bdpmp1"
tb_prefix = 'jos'

def getStore():
    return Store(create_database(db_string))

class BaseStore(object):
   
    def __init__(self, *args, **kwargs):
        self.store = getStore()
        
        #Lazy initialization of the object
        for attribute, value in kwargs.items():
            if not hasattr(self, attribute):
                raise TypeError('unexpected argument %s' % attribute)
            else:
                setattr(self, attribute, value)        

        # divide o dicionario 'convertidos'
        for key in kwargs:
            setattr(self,key,kwargs[key])

        # adiciona a data atual
        self.date_creation = datetime.now()
        
class Conteudo(Storm):
    __storm_table__ = tb_prefix + '_content'
    
    id = Int(primary=True)
    title = Unicode()
    alias = Unicode()
    title_alias = Unicode()
    introtext = Unicode()
    fulltext = Unicode()
    state = Int()
    sectionid = Int()
    mask = Int()
    catid = Int()
    created = DateTime()
    created_by = Int()
    created_by_alias = Unicode()
    modified = DateTime()
    modified_by = Int()
    checked_out = Int()
    checked_out_time = DateTime()
    publish_up = DateTime()
    publish_down = DateTime()
    images = Unicode()
    urls = Unicode()
    attribs = Unicode()
    version = Int()
    parentid = Int()
    ordering = Int()
    metakey = Unicode()
    metadesc = Unicode()
    access = Int()
    hits = Int()
    metadata = Unicode()
    
    def getDateUpdate(self):
        if self.date_updated == None:
            return None
        return self.date_updated.strftime('%d/%m/%Y %H:%M')
        
    def getDateChecked(self):
        return self.date_checked.strftime('%d/%m/%Y %H:%M')
    
    
class Categories(Storm, BaseStore):
    __storm_table__ = tb_prefix + '_categories'
    
    id = Int(primary=True)
    parent_id = Int()
    title = Unicode()
    name = Unicode()
    alias = Unicode()
    image = Unicode()
    section = Unicode()
    image_position = Unicode()
    description = Unicode()
    published = Int()
    checked_out = Int()
    checked_out_time = DateTime()
    editor = Unicode()
    ordering = Int()
    access = Int()
    count = Int()
    params = Unicode()
    
class Menu(Storm, BaseStore):
    __storm_table__ = tb_prefix + '_menu'
    
    id = Int(primary=True)
    menutype = Unicode()
    name = Unicode()
    alias = Unicode()
    link = Unicode()
    type = Unicode()
    published = Int()
    parent = Int()
    componentid = Int()
    
    sublevel = Int()
    ordering = Int()
    checked_out = Int()
    checked_out_time = DateTime()
    pollid = Int()
    browserNav = Int()
    access = Int()
    utaccess = Int()
    params = Unicode()
    lft = Int()
    rgt = Int()
    home = Int()
    
    def getTodosHomologacaoBD(self, ordem='date_homologacao'):
        if ordem == 'usuario':
            data = self.store.find(Homologacao).order_by(Desc(Homologacao.usuario))
        elif ordem == 'id_conteudo':
            data = self.store.find(Homologacao).order_by(Desc(Homologacao.id_conteudo))
        elif ordem == 'date_homologacao':
            data = self.store.find(Homologacao).order_by(Desc(Homologacao.date_homologacao))
        else:
            data = self.store.find(Homologacao).order_by(Desc(Homologacao.id))
            
        if data.count() == 0:
            return None
        else:
            return data
            
    def getDateHomologacao(self):
        if self.date_homologacao == None:
            return None
        return self.date_homologacao.strftime('%d/%m/%Y %H:%M')
    
    def getHomologacaoBD(self, id_conteudo):
        data = self.store.find(Homologacao, Homologacao.id_conteudo==id_conteudo).one()
        if data:
            return data
        else:
            return None
    
    def setHomologacaoBD(self, **kwargs):
        # adicionando...
        try:
            novo_registro = Homologacao(**kwargs)
            self.store.add(novo_registro)
            self.store.flush()
            conteudos = self.store.find(Conteudo,Conteudo.id == novo_registro.id_conteudo)
            for i in conteudos: i.homologado = True;self.store.commit()
            return True
        except:
            print 'Problema ao gravar homologacao: %s' % str(kwargs)
            return False
        
    def delHomologacaoBD(self, id_conteudo):
        result = self.getHomologacaoBD(id_conteudo)
        if result:
            self.store.remove(result)
            self.store.commit()
            return True
        return False