# Import the example MyClass from the conftest module
from conftest import MyClass


def test_hybridmethod():
    """Test the hybridmethod decorator through an example use case of a class providing
    access to a class-level list and instance-level list that are separately held in
    memory and can be added to and removed from without affecting the other, while also
    offering a method that returns a combined list of the items held in both lists."""

    # Ensure that the MyClass type is of the expected type
    assert isinstance(MyClass, type)

    # Ensure that the MyClass type has an items list
    assert isinstance(MyClass.items, list)

    # Ensure that the class' items list is empty to begin with
    assert len(MyClass.items) == 0

    # Add an item to the class' items list
    MyClass.add_item("ABC")

    # Ensure that the class' items list length now reflects the newly added item
    assert len(MyClass.items) == 1

    # Ensure that the class' items list has the expected contents
    assert MyClass.items == ["ABC"]

    # Create an instance of the class
    myclass = MyClass()

    # Ensure that the instance is of the expected type
    assert isinstance(myclass, MyClass)

    # Ensure that the instance has an items list
    assert isinstance(myclass.items, list)

    # Ensure that the instance's items list is empty
    assert len(myclass.items) == 0

    # Add an item to the instance's item list
    myclass.add_item("XYZ")

    # Ensure that the instance's items list length now reflects the newly added item
    assert len(myclass.items) == 1

    # Ensure that the instance's items list has the expected contents
    assert myclass.items == ["XYZ"]

    # Ensure that the instance's items list has the expected contents, in this case
    # as accessed via the class' get_instance_items helper method:
    assert myclass.get_instance_items() == ["XYZ"]

    # Ensure that the class' items list still has the expected contents and was not
    # affected by the addition of an item to the instance's items list, in this case
    # as accessed via the class reference on the instance:
    assert myclass.__class__.items == ["ABC"]

    # Ensure that the class' items list still has the expected contents and was not
    # affected by the addition of an item to the instance's items list, in this case
    # as accessed via the class' get_class_items helper method:
    assert myclass.get_class_items() == ["ABC"]

    # Ensure that the combined items held in the class' and the instance's items list
    # are as expected, in this case as accessed via the items lists directly:
    assert myclass.__class__.items + myclass.items == ["ABC", "XYZ"]

    # Ensure that the combined items held in the class' and the instance's items list
    # are as expected, in this case accessed via the get_combined_items helper method:
    assert myclass.get_combined_items() == ["ABC", "XYZ"]

    # Add another item to the instance's item list
    myclass.add_item(123)

    # Ensure that the class' items list still contains the expected number of items
    assert len(MyClass.items) == 1

    # Ensure that the class' items list still contains the expected items
    assert MyClass.items == ["ABC"]

    # Ensure that the instance's items list contains the expected number of items
    assert len(myclass.items) == 2

    # Ensure that the instance's items list contains the expected items
    assert myclass.items == ["XYZ", 123]

    # Remove an item from the list
    myclass.remove_item("XYZ")

    # Ensure that the instance's items list contains the expected number of items
    assert len(myclass.items) == 1

    # Ensure that the instance's items list contains the expected items
    assert myclass.items == [123]

    # Ensure that the class' items list still contains the expected number of items
    assert len(MyClass.items) == 1

    # Ensure that the class' items list still contains the expected items
    assert MyClass.items == ["ABC"]
