import yaml
import os.path


class NewLoader(yaml.Loader):
    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]
        super(NewLoader, self).__init__(stream)
        NewLoader.add_path_resolver('$ref', NewLoader.ref)
        NewLoader.add_constructor('$include',  NewLoader.ref)
        NewLoader.add_constructor('$import', NewLoader.ref)

    def ref(self, node):
        print(node)
        if isinstance(node, yaml.ScalarNode):
            return self.extractFile(self.construct_scalar(node))

        elif isinstance(node, yaml.SequenceNode):
            result = []
            for filename in self.construct_sequence(node):
                result += self.extractFile(filename)
            return result

        elif isinstance(node, yaml.MappingNode):
            result = {}
            for k,v in self.construct_mapping(node).iteritems():
                result[k] = self.extractFile(v)
            return result

        else:
            print("Error:: unrecognised node type in !include statement")
            raise ValueError("Error:: unrecognised node type in !include statement")

    def extractFile(self, filename):
        filepath = os.path.join(self._root, filename)
        with open(filepath, 'r') as f:
            return yaml.load(f, NewLoader)


if __name__ == '__main__':
    with open('../../logics/logic_river.yaml', 'r') as yml:
        resp = yaml.load(yml, NewLoader)
    print(resp)