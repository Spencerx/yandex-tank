from yandextank.plugins.Telegraf.config_parser import parse_xml, parse_yaml, TARGET_HINT_PLACEHOLDER


class TestConfigParsers(object):
    def test_rawxml_parse(self):
        """ raw xml read from string """
        config = """
        <Monitoring>
            <SshKeyPath>/tmp</SshKeyPath>
            <Host>
                <CPU feature="passed"/>
            </Host>
        </Monitoring>
        """

        host = parse_xml(config)[0]
        assert host.metrics[0].name == 'CPU'
        assert host.ssh_key_path == '/tmp'

    def test_rawxml_parse_without_key_path(self):
        """ raw xml read from string """
        config = """
        <Monitoring>
            <Host>
                <CPU feature="passed"/>
            </Host>
        </Monitoring>
        """

        host = parse_xml(config)[0]
        assert host.metrics[0].name == 'CPU'
        assert host.ssh_key_path is None

    def test_raw_yaml_parse(self):
        """ raw yaml read from string """
        config = """
        ssh_key_path: /tmp
        hosts:
          localhost:
            metrics:
              cpu:
              nstat:
        """
        agents = parse_yaml(config)
        assert agents[0].address == 'localhost'
        host = agents[0]
        assert host.metrics[0].name == 'cpu'
        assert host.metrics[1].name == 'nstat'
        assert host.ssh_key_path == '/tmp'

    def test_raw_yaml_parse_agent_config_is_none(self):
        config = """
        hosts:
          localhost:
        metrics:
          cpu:
          nstat:
        """
        agents = parse_yaml(config)
        assert agents[0].address == 'localhost'
        host = agents[0]
        assert host.metrics[0].name == 'cpu'
        assert host.metrics[1].name == 'nstat'
        assert host.ssh_key_path is None

    def test_raw_yaml_parse_empty_config(self):
        config = ''
        agents = parse_yaml(config)
        assert agents[0].address == TARGET_HINT_PLACEHOLDER
