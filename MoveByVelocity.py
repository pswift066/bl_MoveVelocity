
bl_info = {
    "name": "Move By Velocity",
    "description": "Calculates Positional Moves for Objects with a specified input Velocity",
    "author": "Peter Swift",
    "version": (0,1),
    "blender": (3, 4, 0),
    "location": "View3D > Sidebar",
    "warning": "",
    "category": "Object"
}

import bpy
import mathutils as math

class MovePanel(bpy.types.Panel):
    bl_label = "Move Panel"
    bl_idname = "OBJECT_PT_move_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Move"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.active_object
        
        # X Destination
        row = layout.row()
        row.label(text="X Destination")
        row.prop(scene, "move_x_dest")
        
        # Y Destination
        row = layout.row()
        row.label(text="Y Destination")
        row.prop(scene, "move_y_dest")
        
        # Acceleration
        row = layout.row()
        row.label(text="Acceleration")
        row.prop(scene, "move_accel")
        
        # Velocity
        row = layout.row()
        row.label(text="Velocity")
        row.prop(scene, "move_vel")
        
        # Insert Move button
        row = layout.row()
        row.operator("object.insert_move", text="Insert Move")

def register():
    bpy.utils.register_class(MovePanel)
    bpy.types.Scene.move_x_dest = bpy.props.FloatProperty(name="X Destination", default=0.0)
    bpy.types.Scene.move_y_dest = bpy.props.FloatProperty(name="Y Destination", default=0.0)
    bpy.types.Scene.move_accel = bpy.props.FloatProperty(name="Acceleration", default=1.0)
    bpy.types.Scene.move_vel = bpy.props.FloatProperty(name="Velocity", default=1.0)
    bpy.utils.register_class(OBJECT_OT_insert_move)

def unregister():
    bpy.utils.unregister_class(MovePanel)
    del bpy.types.Scene.move_x_dest
    del bpy.types.Scene.move_y_dest
    del bpy.types.Scene.move_accel
    del bpy.types.Scene.move_vel
    bpy.utils.unregister_class(OBJECT_OT_insert_move)



class OBJECT_OT_insert_move(bpy.types.Operator):
    bl_idname = "object.insert_move"
    bl_label = "Insert Move"

    def execute(self, context):

        scene = bpy.context.scene
        obj = bpy.context.object

        timestep = 1 / scene.render.fps

        # Initialize dynamics

        input_acceleration = context.scene.move_vel
        input_velocity = context.scene.move_accel

        destination_position = math.Vector((context.scene.move_x_dest,context.scene.move_y_dest,0))
        starting_position = obj.location.copy()
        current_position = starting_position
        starting_velocity = math.Vector((0,0,0))
        current_velocity = starting_velocity

        motion_direction = destination_position - current_position
        move_distance = motion_direction.length
        motion_direction = motion_direction.normalized()

        # Calculate trapezoid move parameters

        d1 = ( input_velocity ** 2 ) / ( 2 * input_acceleration )
        d3 = d1
        d2 = move_distance - ( d1 + d3 )

        # how many frames do we need to calculate?

        l1 = input_velocity / input_acceleration
        l2 = d2 / input_velocity
        l3 = l1
        ltotal = l1 + l2 + l3

        frame_total = ltotal * scene.render.fps

        obj.location = current_position
        bpy.context.view_layer.update()
        bpy.ops.anim.keyframe_insert(type='BUILTIN_KSI_LocRot')

        for frames in range(scene.frame_current + 1,int(frame_total)+scene.frame_current):

            remaining_distance = destination_position - current_position
            remaining_distance = remaining_distance.length

            scene.frame_set(frames)

            if remaining_distance >= ( d2 + d3 ):
                # movement phase 1
                current_velocity += motion_direction * input_acceleration * timestep
            elif remaining_distance > d3:
                # movement phase 2
                current_velocity.normalize()
                current_velocity *= input_velocity
            else:
                # movement phase 3
                current_velocity -= motion_direction * input_acceleration * timestep

            print("current velocity = " + str(current_velocity.length))    
            current_position += current_velocity * timestep

            obj.location = current_position
            bpy.context.view_layer.update()
            bpy.ops.anim.keyframe_insert(type='BUILTIN_KSI_LocRot')

        scene.frame_set(scene.frame_current + 1)
        current_position = destination_position
        
        return {'FINISHED'}

if __name__ == "__main__":
    register()
