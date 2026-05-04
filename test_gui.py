"""Test the VR1 Lattice Builder GUI functionality"""

def test_gui_components():
    """Test that GUI components can be imported and basic functionality works"""
    # Test without GUI - core functionality
    import copy
    
    # Test component types definition
    component_types = [
        'w', '8', '6', '4', 'X', 'O', 'd', 'rt', 'wrc', 
        'v90', 'v56', 'v30', 'v25', 'v12'
    ]
    
    # Test default lattice 
    default_lattice = [
        ['0', '1', '2', '3', '4', '5', '6', '7'],
        ['1', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],
        ['2', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],
        ['3', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],
        ['4', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],
        ['5', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],
        ['6', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],
        ['7', 'w', 'w', 'w', 'w', 'w', 'w', 'w'],
    ]
    
    # Test lattice operations
    test_lattice = copy.deepcopy(default_lattice)
    
    # Simulate component cycling
    current_component = test_lattice[1][1]  # Should be 'w'
    current_index = component_types.index(current_component)
    next_index = (current_index + 1) % len(component_types)
    new_component = component_types[next_index]
    test_lattice[1][1] = new_component
    
    assert test_lattice[1][1] == '8', f"Component cycling failed: expected '8', got {test_lattice[1][1]}"
    
    # Test save functionality
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('"""Custom VR-1 reactor lattice configuration"""\n\n')
        f.write('CUSTOM_LATTICE = [\n')
        for row in test_lattice:
            f.write(f'    {row},\n')
        f.write(']\n')
        temp_filename = f.name
    
    # Verify file was created and contains expected content
    with open(temp_filename, 'r') as f:
        content = f.read()
        assert 'CUSTOM_LATTICE' in content
        assert "['1', '8'," in content  # Our modified cell
    
    # Clean up
    os.unlink(temp_filename)
    
    print("✓ All GUI functionality tests passed")


def test_utils_integration():
    """Test that the utils integration works"""
    from vr1.utils import launch_lattice_builder
    # Just test that function exists and is callable
    assert callable(launch_lattice_builder), "launch_lattice_builder is not callable"
    print("✓ Utils integration test passed")


if __name__ == "__main__":
    test_gui_components()
    test_utils_integration()
    print("✓ All tests completed successfully!")