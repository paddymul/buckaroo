from buckaroo.buckaroo_widget import BuckarooWidget

def reacton_buckaroo(**kwargs):
    import reacton
    widget_cls = BuckarooWidget
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return reacton.core.Element(comp, kwargs=kwargs)

#use buckaroo like this
'''
import pandas as pd
import solara

df = pd.DataFrame({'a':[10,20]})
@solara.component
def Page():
    bw = reacton_buckaroo(df=df)
Page()
'''
