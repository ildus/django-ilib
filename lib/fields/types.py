#coding: utf-8

class Money:
    def __init__(self, value = None):
        if type(value) not in [int, float]:
            raise ValueError()
        
        self.value = value*100000
        
    def __unicode__(self):
        return "%f RUR"%(self.value / 100000)