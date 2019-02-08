import pytest


class NestedObject(object):
    pykka_traversable = True
    inner = 'nested.inner'


@pytest.fixture(scope='module')
def actor_class(runtime):
    class ActorA(runtime.actor_class):
        an_attr = 'an_attr'
        _private_attr = 'secret'
        nested = NestedObject()

        @property
        def a_ro_property(self):
            return 'a_ro_property'

        _a_rw_property = 'a_rw_property'

        @property
        def a_rw_property(self):
            return self._a_rw_property

        @a_rw_property.setter
        def a_rw_property(self, value):
            self._a_rw_property = value

    return ActorA


@pytest.fixture
def proxy(actor_class):
    proxy = actor_class.start().proxy()
    yield proxy
    proxy.stop()


def test_actor_attr_can_be_read_using_get_postfix(proxy):
    assert proxy.an_attr.get() == 'an_attr'


def test_actor_attr_can_be_set_using_assignment(proxy):
    assert proxy.an_attr.get() == 'an_attr'

    proxy.an_attr = 'an_attr_2'

    assert proxy.an_attr.get() == 'an_attr_2'


def test_private_attr_access_raises_exception(proxy):
    with pytest.raises(AttributeError):
        proxy._private_attr.get()


def test_actor_property_can_be_read_using_get_postfix(proxy):
    assert proxy.a_ro_property.get() == 'a_ro_property'
    assert proxy.a_rw_property.get() == 'a_rw_property'


def test_actor_property_can_be_set_using_assignment(proxy):
    proxy.a_rw_property = 'a_rw_property_2'

    assert proxy.a_rw_property.get() == 'a_rw_property_2'


def test_actor_read_only_property_cannot_be_set(proxy):
    with pytest.raises(AttributeError):
        proxy.a_ro_property = 'a_ro_property_2'


def test_actor_with_mock_attribute_works(runtime, mocker):
    class Actor(runtime.actor_class):
        attr = mocker.Mock()

    actor_ref = Actor.start()
    try:
        actor_ref.proxy()
    finally:
        actor_ref.stop()


def test_actor_with_mocked_method_works(runtime, mocker):
    class Actor(runtime.actor_class):
        def do_it(self):
            pass

    with mocker.patch.object(Actor, 'do_it') as mock:
        actor_ref = Actor.start()
        try:
            actor_ref.proxy()
        finally:
            actor_ref.stop()

        assert mock.call_count == 0


def test_attr_of_traversable_attr_can_be_read(proxy):
    assert proxy.nested.inner.get() == 'nested.inner'
