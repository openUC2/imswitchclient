#%%
import imswitchclient.ImSwitchClient as imc


# Instantiate the ImSwitchClient
client = imc.ImSwitchClient()
#%%
# Test the get_positioner_names method
positioner_names = client.get_positioner_names()
print("Positioner Names:", positioner_names)
#%%
#
# Test the move_positioner method
positioner_name = positioner_names[0]
axis = "X"
dist = 1000
is_absolute = True
is_blocking = False

response = client.move_positioner(positioner_name, axis, dist, is_absolute, is_blocking)
print("Move Positioner Response:", response)

#%%
# Test the snap_numpy_to_fastapi method
image_array = client.snap_numpy_to_fastapi()
print("Image Array Shape:", image_array.shape)



