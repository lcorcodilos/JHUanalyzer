import sys
sys.path.append('../')
from Tools.Common import GetHistBinningTuple, CompileCpp

import clang.cindex
cpp_idx = cindex.Index.create()
cpp_args =  '-x c++ --std=c++11'.split()

#####################
# Corrections class #
#####################
class Correction(object):
    def __init__(self,name,script,mainFunc=None,corrtype=None,isClone=False):
        self.name = name
        self.script = script
        self.type = self._getType()
        self.funcInfo = self._getFuncInfo()
        self.funcNames = self.funcInfo.keys()
        self.mainFunc = mainFunc

        if not isClone:
            if mainFunc != None and self.mainFunc not in self.funcNames:
                raise ValueError('ERROR: Correction() instance provided with mainFunc argument that does not exist in %s'%self.script)
            if len(self.funcNames) == 1: self.mainFunc = self.funcNames[0]

            script_file = open(script,'r')
            CompileCpp(script)

    # If multiple functions in the same script, can clone and reassign mainFunc
    def Clone(self,newname,newMainFunc=self.mainFunc):
        return Correction(newname,self.script,newMainFunc,corrtype=self.type,isClone=True)

    def _getType(self):
        self.type = None
        if corrtype in ['weight','uncert']:
            self.type = corrtype
        elif corrtype not in ['weight','uncert'] and corrtype != None:
            print ('WARNING: Correction type %s is not accepted. Only "weight" or "uncert". Will attempt to resolve...')

        if self.type == None:
            if '_weight.cc' in self.script or '_SF.cc' in self.script:
                self.type = 'weight'
            elif '_uncert.cc' in self.script:
                self.type = 'uncert'
            else:
                raise ValueError('ERROR: Attempting to add correction "%s" but script name (%s) does not end in "_weight.cc", "_SF.cc" or "_uncert.cc" and so the type of correction cannot be determined.'%(name))

    def _getFuncInfo(self):
        translation_unit = cpp_idx.parse(self.script, args=cpp_args)
        filename = translation_unit.cursor.spelling
        funcs = OrderedDict()
        # Walk cursor over script
        for c in translation_unit.cursor.walk_preorder():
            # Pass over file errors
            if c.location.file is None: pass
            elif c.location.file.name != filename: pass
            else:
                # Check for namespace with functions inside
                if c.kind == cindex.CursorKind.NAMESPACE:
                    # Loop over children of namespace
                    for child in c.get_children():
                        # If a function, store a name as key with namespace included (does not support nested namespaces)
                        if child.kind == cindex.CursorKind.FUNCTION_DECL:
                            funcname = c.spelling+'::'+child.spelling
                            # If we haven't accounted for it, store key as arg name and value as the type
                            if funcname not in funcs.keys():
                                funcs[funcname] = OrderedDict()
                                for arg in child.get_arguments():
                                    funcs[funcname][arg.spelling] = arg.type.spelling 
                # Check for functions
                elif c.kind == cindex.CursorKind.FUNCTION_DECL:
                    func_exists = False
                    # Check it wasn't already found in the namespace
                    for existing_func in funcs.keys():
                        this_func = c.spelling
                        if this_func in existing_func:
                            func_exists = True
                    # If we haven't accounted for it, store key as arg name and value as the type
                    if not func_exists:
                        funcs[c.spelling] = OrderedDict()
                        for arg in c.get_arguments():
                            funcs[c.spelling][arg.spelling] = arg.type.spelling

        return funcs

    def GetCall(self):
        out = '%s('
        for a in self.funcInfo[self.mainFunc].keys():
            out += '%s,'%(self.funcInfo[self.mainFunc][a],a)
        out = out[:-1]+')'

        return out

    def SetMainFunc(self,funcname):
        # Find funcname in case it's abbreviated (which it might be if the user forgot the namespace)
        full_funcname = ''
        for f in self.funcNames:
            if funcname in f:
                full_funcname = f
                break

        if full_funcname not in self.funcNames:
            raise ValueError('ERROR: Function name "%s" is not defined for %s'%(funcname,self.script))

        self.mainFunc = full_funcname
        return self

    def GetMainFunc(self):
        return self.mainFunc

    def GetType(self):
        return self.type