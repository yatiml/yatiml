# Example from https://github.com/GooglingTheCancerGenome/sv-gen

class Genotype(enum.Enum):
    HOMO_NOSV = 'hmz'
    HOMO_SV = 'hmz-sv'
    HETERO_SV = 'htz-sv'

    @classmethod
    def yatiml_savorize(cls, node: yatiml.Node) -> None:
        # enum.Enum has a __members__ attribute which contains its
        # members, which we reverse here to make a look-up table that
        # converts values in the YAML file to names expected by YAtiML.
        yaml_to_python = {
                v.value: v.name for v in cls.__members__.values()}

        # Remember that the node can be anything here. We only convert
        # if it's a string with an expected value, otherwise we leave
        # it alone so that a useful error message can be generated.
        if node.is_scalar(str):
            if node.get_value() in yaml_to_python:
                node.set_value(yaml_to_python[node.get_value()])

    @classmethod
    def yatiml_sweeten(cls, node: yatiml.Node) -> None:
        # Here we just use cls.__members__ directly to convert.
        node.set_value(cls.__members__[node.get_value()].value)
