from pyparsing import (
    Word,
    alphanums,
    Suppress,
    Optional,
    pyparsing_common,
    OneOrMore,
    Group, White
)


datatypes = {'positiveInteger':'xsd:positiveInteger',
             'nonPositiveInteger':'xsd:nonPositiveInteger',
             'nonNegativeInteger':'xsd:nonNegativeInteger',
             'negativeInteger':'xsd:ngativeInteger',
             'integer':'xsd:integer',
             'decimal':'xsd:decimal',
             'dateTime':'xsd:dateTime',
             'boolean':'xsd:boolean'}

# Add my nuclear grammar elements
# An identifier is a word composed by alphanumericals and _$
ident = Word(alphanums + "_$")


requirement = Optional(Word('have') + Suppress(White(" ")))('dataproperty') + ident('TargetPath') + Optional(Word('by'))('inverse') + Optional(Suppress('at least') + pyparsing_common.integer('minCount')) \
              + Optional(Suppress(','))+ Optional(Suppress('maximum of') + pyparsing_common.integer('maxCount')) + Optional(ident('SubjectType')) + Optional(Suppress('and'))

Specification = Group(ident('ShapeName') + Suppress(':') + Suppress('Every') + ident('TargetClass') + Suppress('should') + OneOrMore(Group(requirement)) + Suppress('.'))

SpecificationList = OneOrMore(Specification)
#
def write_shacl(string):
    parsing_result = SpecificationList.parse_string(string)
    def translatePropertyShape(prop_shape,inverse=False,dataproperty=False):
        if not inverse:
            t = f"""
sh:property [
sh:path brick:{prop_shape['TargetPath']} ;
 """
            t += ' ; \n '.join([f'sh:{key} {prop_shape[key]}' for key in prop_shape if not key in ['TargetPath',
                                                                                                  'SubjectType',
                                                                                                  'inverse',
                                                                                                  'dataproperty'
                                                                                                  ]])
        else:
            t = f"""    sh:property [
    sh:path [sh:inversePath brick:{prop_shape['TargetPath']}] ;
"""
            t += ' ; \n'.join([f'sh:{key} {prop_shape[key]}' for key in prop_shape if not key in ['TargetPath',
                                                                                                  'SubjectType',
                                                                                                  'inverse',
                                                                                                  'dataproperty'
                                                                                                  ]])
        if 'SubjectType' in prop_shape and dataproperty:
            t += f' ;\n\tsh:datatype {datatypes.get(prop_shape["SubjectType"])}'
        elif 'SubjectType' in prop_shape and not dataproperty:
            t += f' ;\n\tsh:class brick:{prop_shape["SubjectType"]}'
        return t

    s = f"""
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix inst: <http://linkedbuildingdata.net/ifc/resources20201208_005325/> .
@prefix brick: <https://brickschema.org/schema/Brick#> ."""

    def translateSpecification(specification):
        sp = f"""
inst:{specification['ShapeName']} a sh:NodeShape ;
    sh:targetClass brick:{specification['TargetClass']} ;
"""
        if len(specification) > 2:
            sp += ' ;] ;\n'.join([translatePropertyShape(specification[i].asDict(),
                                            'inverse' in specification[i].asDict(),
                                            'dataproperty' in specification[i].asDict()) for i in range(2,len(specification))])

        sp += ' ;\n] .'
        return sp

    s += '\n'.join([translateSpecification(spec) for spec in parsing_result])

    return s

if __name__ == '__main__':
    test_1 = """R1 : Every VAV should hasPoint at least 1 Zone_Air_Temperature_Sensor and hasPoint at least 1 Zone_Air_Temperature_Setpoint.
        R2 : Every HVAC_Zone should feeds by at least 1 VAV.
        R3 : Every HVAC_Zone should hasPoint at least 2."""


    print(write_shacl(test_1))


