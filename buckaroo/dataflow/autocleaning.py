import pandas as pd
from buckaroo.jlisp.lisp_utils import split_operations
from buckaroo.jlisp.lispy import s
from buckaroo.pluggable_analysis_framework.analysis_management import DfStats
from ..customizations.all_transforms import configure_buckaroo, DefaultCommandKlsList

def dumb_merge_ops(existing_ops, cleaning_ops):
    """ strip cleaning_ops from existing_ops, reinsert cleaning_ops at the beginning """
    a = existing_ops.copy()
    a.extend(cleaning_ops)
    return a

SENTINEL_DF_1 = pd.DataFrame({'foo'  :[10, 20], 'bar' : ["asdf", "iii"]})
SENTINEL_DF_2 = pd.DataFrame({'col1' :[55, 55], 'col2': ["pppp", "333"]})
SENTINEL_DF_3 = pd.DataFrame({'pp'   :[99, 33], 'ee':   [     6,     9]})
SENTINEL_DF_4 = pd.DataFrame({'vvv'  :[12, 49], 'oo':   [ 'ccc', 'www']})

class SentinelAutocleaning:

    def __init__(self, confs):
        self.commandConfig = {}
    
    def handle_ops_and_clean(self, df, cleaning_method, existing_operations):
        cleaning_ops = []
        generated_code = ""
        if cleaning_method == "one op":
            cleaning_ops =  [""]
            generated_code = "codegen 1"
            generated_code = "codegen 2"
        elif cleaning_method == "two op":
            cleaning_ops = ["", ""]

        merged_operations = dumb_merge_ops(existing_operations, cleaning_ops)
        
        if len(merged_operations) == 1:
            cleaned_df = SENTINEL_DF_1
        elif len(merged_operations) == 2:
            cleaned_df = SENTINEL_DF_2
        else:
            cleaned_df = df
        return [cleaned_df, {}, generated_code, merged_operations]

def merge_ops(existing_ops, cleaning_ops):
    """ strip cleaning_ops from existing_ops, reinsert cleaning_ops at the beginning """
    old_cleaning_ops, user_gen_ops = split_operations(existing_ops)
    merged = cleaning_ops.copy()
    merged.extend(user_gen_ops)  # we want the user cleaning ops to come last
    return merged



def format_ops(column_meta):
    """
    translate summary_dict with cleaning_ops to real, usable instructions
    """
    ret_ops = []
    for k,v in column_meta.items():
        if k == 'index':
            continue
        if 'cleaning_ops' not in v:
            continue
        ops = v['cleaning_ops']
        if len(ops) > 0:
            temp_ops = ops.copy()
            temp_ops.insert(2, k)
            ret_ops.append(temp_ops)
    return ret_ops

class AutocleaningConfig:
    command_klasses = [DefaultCommandKlsList]
    autocleaning_analysis_klasses = []

    name = 'default'
    

class PandasAutocleaning:
    # def add_command(self, incomingCommandKls):
    #     without_incoming = [x for x in self.command_classes if not x.__name__ == incomingCommandKls.__name__]
    #     without_incoming.append(incomingCommandKls)
    #     self.command_klasses = without_incoming
    #     self.setup_from_command_kls_list()

    DFStatsKlass = DfStats
    #until we plumb in swapping configs, just stick with default
    def __init__(self, ac_configs=tuple([AutocleaningConfig()]), conf_name="default"):

        self.config_dict = {}
        for conf in ac_configs:
            self.config_dict[conf.name] = conf
        self._setup_from_command_kls_list(conf_name)

    ### start code interpreter block
    def _setup_from_command_kls_list(self, name):
        #used to initially setup the interpreter, and when a command
        #is added interactively
        if name not in self.config_dict:
            options = list(self.config_dict.keys())
            raise Exception(
                "Unknown autocleaning conf of %s, available options are %r" % (name, options))
        conf = self.config_dict[name]
        c_klasses, self.autocleaning_analysis_klasses = conf.command_klasses, conf.autocleaning_analysis_klasses

        c_defaults, c_patterns, df_interpreter, gencode_interpreter = configure_buckaroo(c_klasses)
        self.df_interpreter, self.gencode_interpreter = df_interpreter, gencode_interpreter
        self.commandConfig = dict(argspecs=c_patterns, defaultArgs=c_defaults)


    def _run_df_interpreter(self, df, operations):
        full_ops = [{'symbol': 'begin'}]

        def wrap_set_df(form):
            """
            wrap each passed in form with a set! call to update the df symbol
            """
            return [s("set!"), s("df"), form]
        full_ops.extend(map(wrap_set_df, operations))
        full_ops.append(s("df"))
        if len(full_ops) == 1:
            return df
        
        return self.df_interpreter(full_ops , df)

    def _run_code_generator(self, operations):
        if len(operations) == 0:
            return 'no operations'
        return self.gencode_interpreter(operations)

    def _run_cleaning(self, df, cleaning_method):
        dfs = self.DFStatsKlass(df, self.autocleaning_analysis_klasses, debug=True)
        gen_ops = format_ops(dfs.sdf)

        #cleaning_sd = {}
        return gen_ops, dfs.sdf

    @staticmethod
    def make_origs(raw_df, cleaned_df, cleaning_sd):
        cols = {}

        changed = 0
        for col, sd in cleaning_sd.items():
            if col not in cleaned_df.columns:
                continue
            if col == 'index':
                continue
            if "add_orig" in sd:
                cols[col] = cleaned_df[col]
                cols[col + "_orig"] = raw_df[col]
                changed += 1
            else:
                cols[col] = cleaned_df[col]
        if changed > 0:
            return pd.DataFrame(cols)
        else:
            return cleaned_df

    def handle_ops_and_clean(self, df, cleaning_method, existing_operations):
        if df is None:
            #on first instantiation df is likely to be None,  do nothing and return
            return None
        if cleaning_method == "" and len(existing_operations) == 0:
            #no cleaning method was specified, just return the bare minimum
            return [df, {},  "#empty generated code", merge_ops(existing_operations, [])]
        self._setup_from_command_kls_list(cleaning_method)
        cleaning_operations, cleaning_sd = self._run_cleaning(df, cleaning_method)
        merged_operations = merge_ops(existing_operations, cleaning_operations)
        cleaned_df = self._run_df_interpreter(df, merged_operations)
        #print("len(cleaned_df)", len(cleaned_df))
        merged_cleaned_df = self.make_origs(df, cleaned_df, cleaning_sd)
        generated_code = self._run_code_generator(merged_operations)
        #print(f"{merged_cleaned_df=}, {type(merged_cleaned_df)=}")

        return [merged_cleaned_df, cleaning_sd, generated_code, merged_operations]
