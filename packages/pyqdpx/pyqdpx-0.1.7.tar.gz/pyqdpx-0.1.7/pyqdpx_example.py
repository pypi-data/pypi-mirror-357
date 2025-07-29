'''
Example usage and testing of the pyqdpx library.
'''

from pyqdpx import QDPX, User, Code
import uuid
import zipfile
import os

def create_dummy_qdpx_file(filename="test.qdpx"):
    """
    Helper function to create a dummy QDPX zip file for testing purposes,
    including a more complex CodeBook structure.
    """
    project_xml_content = f"""<?xml version="1.0" encoding="utf-8"?>
<Project>
    <Metadata>
        <Title>My Test Project</Title>
    </Metadata>
    <Users>
        <User guid="4c35014e-8fa9-4e47-b5d1-bfc14a8ddf4f" id="SF" name="Florian Sipos"/>
        <User guid="736b0968-f379-4f6d-80d0-479bfa4439b9" id="DS" name="domonkos sik"/>
    </Users>
    <CodeBook>
        <Codes>
            <Code guid="3c51efbb-071f-43a7-9f32-228b89668e8d" name="1. Perceived Susceptibility" isCodable="true">
                <Description>Az emberek akkor hajlandók cselekedni, ha hisznek abban, hogy ők is veszélyben vannak.</Description>
                <Code guid="8baf0c83-56c4-4dc8-9e5b-cf6d6073bdb5" name="alacsony fogékonyság" isCodable="true" />
                <Code guid="b3bae912-0f40-4549-8e8f-dd46acd4f161" name="csoportszintű fogékonyság" isCodable="true" />
            </Code>
            <Code guid="aee8e423-1848-4192-84cf-ea6cb669ff61" name="11. Identitások" isCodable="true">
                <Code guid="ff40617f-1ccd-4e9b-9d15-0ad0801e0d44" name="szélsőjobb" isCodable="true" />
            </Code>
            <Code guid="{str(uuid.uuid4())}" name="Top Level Code 1" isCodable="true" />
        </Codes>
    </CodeBook>
    <OtherData>Some other XML data</OtherData>
</Project>
"""
    source1_content = "This is the content of source 1."
    source2_content = "This is source 2, with more data."
    florian_source_content = "Content for Florian's source."

    with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('project.qde', project_xml_content.encode('utf-8'))
        zf.writestr('Sources/source1.txt', source1_content.encode('utf-8'))
        zf.writestr('Sources/source2.txt', source2_content.encode('utf-8'))
        zf.writestr('Sources/4c35014e-8fa9-4e47-b5d1-bfc14a8ddf4f.txt', florian_source_content.encode('utf-8'))
    print(f"Created dummy QDPX file: {filename}")

def cleanup_dummy_qdpx_file(filename="test.qdpx"):
    """
    Helper function to remove the dummy QDPX file after testing.
    """
    if os.path.exists(filename):
        os.remove(filename)
        print(f"Cleaned up dummy QDPX file: {filename}")

def run_example():
    """
    Demonstrates the usage of the QDPX, QDE, and User and Code classes.
    """
    test_zip_filename = "test.qdpx"
    
    print("\n--- Creating a dummy QDPX file for testing ---")
    create_dummy_qdpx_file(test_zip_filename)

    print("\n--- Initializing QDPX object ---")
    qdpx_file = QDPX(test_zip_filename)

    print("\n--- Listing sources ---")
    sources = qdpx_file.list_sources()
    print(f"Sources found: {sources}")
    # Assertions to verify expected output
    assert 'source1.txt' in sources
    assert 'source2.txt' in sources
    assert '4c35014e-8fa9-4e47-b5d1-bfc14a8ddf4f.txt' in sources

    print("\n--- Getting content of a specific source ---")
    guid_for_source = "4c35014e-8fa9-4e47-b5d1-bfc14a8ddf4f"
    source_content = qdpx_file.get_source(guid_for_source)
    print(f"Content of '{guid_for_source}.txt':\n{source_content}")
    assert source_content == "Content for Florian's source."

    print("\n--- Getting project.qde ---")
    project = qdpx_file.get_project()
    assert project is not None
    print(f"Is project modified initially? {project.modified}")
    assert not project.modified # Should be False initially

    # User section

    print("\n--- Listing initial users in the project ---")
    initial_users = project.users
    for user in initial_users:
        print(initial_users[user])
    assert len(initial_users) == 2
    # Check if the initial users are correctly loaded
    assert User(guid='4c35014e-8fa9-4e47-b5d1-bfc14a8ddf4f', id='SF', name='Florian Sipos') in initial_users.values()
    assert User(guid='736b0968-f379-4f6d-80d0-479bfa4439b9', id='DS', name='domonkos sik') in initial_users.values()


    print("\n--- Adding a new user (GUID generated automatically) ---")
    new_user_1 = User(id="JA", name="Jane Austen") 
    project.add_user(new_user_1)
    print(f"New user added: {new_user_1}")
    print(f"Is project modified after adding user? {project.modified}")
    assert project.modified # Should be True after modification

    print("\n--- Verifying user list after adding (in memory) ---")
    current_users = project.users
    print("Users after adding (in memory):")
    for user in current_users:
        print(current_users[user])
    assert len(current_users) == 3
    assert new_user_1 in current_users.values()
    assert new_user_1.guid in current_users  # Check if the new user's GUID is in the dict
    assert current_users[new_user_1.guid] == new_user_1  # Ensure the user object matches

    print("\n--- Adding another new user with a specified GUID ---")
    try:
        new_user_2 = User(id="HB", name="Homer B Simpson", guid="a1b2c3d4-e5f6-7890-abcd-1234567890ab")
        project.add_user(new_user_2)
        print(f"New user added: {new_user_2}")
        print(f"Is project modified after adding second user? {project.modified}")
        assert project.modified # Still True as more changes were made
    except ValueError as e:
        print(f"Error creating user with specified GUID: {e}")
        assert False, "Failed to add user with valid specified GUID."


    print("\n--- Saving the modified project to the zip file ---")
    project.save()

    print("\n--- Re-opening the QDPX file to verify saved changes ---")
    # Crucially, invalidate the cached project object so QDPX reloads it from the updated disk file
    qdpx_file._qde_project = None
    reloaded_project = qdpx_file.get_project()
    assert reloaded_project is not None
    print(f"Is reloaded project modified? {reloaded_project.modified}")
    assert not reloaded_project.modified # Should be False after saving and reloading

    print("\n--- Listing users from the reloaded project ---")
    reloaded_users = reloaded_project.users
    print("Users in reloaded project:")
    for user in reloaded_users:
        print(reloaded_users[user])
    assert len(reloaded_users) == 4 # Original 2 + 2 new users
    assert new_user_1 in reloaded_users.values()
    assert new_user_2 in reloaded_users.values()

    print("\n--- Testing invalid GUID creation for User class ---")
    try:
        invalid_user = User(id="XX", name="Invalid GUID Test", guid="not-a-valid-guid")
        assert False, "ValueError was not raised for an invalid GUID."
    except ValueError as e:
        print(f"Successfully caught expected error for invalid GUID: {e}")

    print("\n--- Cleaning up dummy QDPX file ---")
    cleanup_dummy_qdpx_file(test_zip_filename)

    print("\n--- All demonstrated functionalities and tests passed! ---")

    print("\n--- Creating a dummy QDPX file for testing ---")
    create_dummy_qdpx_file(test_zip_filename)

    print("\n--- Initializing QDPX object ---")
    qdpx_file = QDPX(test_zip_filename)

    print("\n--- Getting project.qde ---")
    project = qdpx_file.get_project()

    print("\n--- Loading and printing initial code tree ---")
    # Accessing .codes property will trigger the parsing from XML
    codes = project.codes 
    project.print_code_tree()
    print(f"Total codes loaded: {len(codes)}")
    assert len(codes) == 6 # 3 top-level + 3 children

    print("\n--- Finding a specific code ---")
    susceptibility_code = project.find_code("1. Perceived Susceptibility")
    if susceptibility_code:
        print(f"Found code: {susceptibility_code.name}, Description: {susceptibility_code.description}")
        assert susceptibility_code.description is not None
        assert susceptibility_code.guid == "3c51efbb-071f-43a7-9f32-228b89668e8d"
    else:
        print("Code '1. Perceived Susceptibility' not found.")
        assert False

    print("\n--- Modifying a code's name and description ---")
    if susceptibility_code:
        old_name = susceptibility_code.name
        old_desc = susceptibility_code.description
        susceptibility_code.name = "1. Perceived Susceptibility (Modified)"
        susceptibility_code.description = "Updated description for susceptibility."
        print(f"Code name changed from '{old_name}' to '{susceptibility_code.name}'")
        print(f"Code description changed from '{old_desc}' to '{susceptibility_code.description}'")
        print(f"Is project modified after code modification? {project.modified}")
        assert project.modified # Should be True

    print("\n--- Adding a new top-level code ---")
    new_top_code = Code(name="New Top Level Category", qde_instance=project, is_codable=True, description="A brand new top-level code.")
    print(f"Added new top-level code: {new_top_code}")
    print(f"Is project modified after adding new code? {project.modified}")
    assert project.modified

    print("\n--- Adding a child code to an existing code (e.g., to '11. Identitások') ---")
    identities_code = project.find_code("11. Identitások")
    if identities_code:
        new_child_code = Code(name="new identity type", qde_instance=project, parent=identities_code)
        print(f"Added new child code: {new_child_code} to parent {identities_code.name}")
        print(f"Parent's children: {[c.name for c in identities_code.children]}")
        assert new_child_code.parent == identities_code
        assert new_child_code in identities_code.children
    else:
        print("Could not find '11. Identitások' to add child code.")
        assert False

    print("\n--- Attempting to delete a code with children (should fail) ---")
    try:
        if identities_code:
            identities_code.delete()
        assert False, "Deletion of code with children did not raise an exception."
    except Exception as e:
        print(f"Successfully caught expected error: {e}")

    print("\n--- Deleting a leaf-node code (e.g., 'alacsony fogékonyság') ---")
    low_susceptibility_code = project.find_code("alacsony fogékonyság")
    if low_susceptibility_code:
        parent_of_low_sus = low_susceptibility_code.parent
        if parent_of_low_sus:
            print(f"Parent of 'alacsony fogékonyság' before deletion: {parent_of_low_sus.name}, children: {[c.name for c in parent_of_low_sus.children]}")
        
        low_susceptibility_code.delete()
        print(f"Is project modified after deleting code? {project.modified}")
        assert project.modified
        
        # Verify it's gone from the parent's children list
        if parent_of_low_sus:
            print(f"Parent of 'alacsony fogékonyság' after deletion: {parent_of_low_sus.name}, children: {[c.name for c in parent_of_low_sus.children]}")
            assert "alacsony fogékonyság" not in [c.name for c in parent_of_low_sus.children]
        
        # Verify it's gone from the main codes dict
        assert low_susceptibility_code.guid not in project.codes
    else:
        print("Code 'alacsony fogékonyság' not found for deletion.")
        assert False

    print("\n--- Saving the modified project to the zip file ---")
    qdpx_file.save_project()

    print("\n--- Re-opening the QDPX file to verify saved changes ---")
    # Crucially, invalidate the cached project object so QDPX reloads it from the updated disk file
    qdpx_file._qde_project = None
    reloaded_project = qdpx_file.get_project()
    assert reloaded_project is not None
    print(f"Is reloaded project modified? {reloaded_project.modified}")
    assert not reloaded_project.modified # Should be False after saving and reloading

    print("\n--- Printing reloaded code tree ---")
    reloaded_project.print_code_tree()
    print(f"Total codes after reload: {len(reloaded_project.codes)}")
    # Assert expected number of codes after adding 2 and deleting 1: 6 - 1 + 2 = 7
    assert len(reloaded_project.codes) == 7

    print("\n--- Verifying a modified code's name and description from reloaded project ---")
    reloaded_susceptibility = reloaded_project.find_code("1. Perceived Susceptibility (Modified)")
    if reloaded_susceptibility:
        print(f"Reloaded code name: {reloaded_susceptibility.name}")
        print(f"Reloaded code description: {reloaded_susceptibility.description}")
        assert reloaded_susceptibility.name == "1. Perceived Susceptibility (Modified)"
        assert reloaded_susceptibility.description == "Updated description for susceptibility."
    else:
        print("Modified code '1. Perceived Susceptibility (Modified)' not found in reloaded project.")
        assert False

    print("\n--- Cleaning up dummy QDPX file ---")
    # cleanup_dummy_qdpx_file(test_zip_filename)

    print("\n--- All demonstrated functionalities and tests passed! ---")

# Execute the example when the script is run directly
if __name__ == "__main__":
    run_example()
