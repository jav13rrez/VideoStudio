import bpy, json, math
from mathutils import Vector

R = "\\\\wsl.localhost\\Ubuntu\\home\\jav13rrez\\VideoStudio\\biblioteca\\personajes\\"
RJ = "//wsl.localhost/Ubuntu/home/jav13rrez/VideoStudio/biblioteca/personajes/"
PAD = 7          # margen que el contorno añade a cada lado de los cuerpos
PAD_CABEZA = 22
ESC_CUERPO_TUTOR = 0.001106   # m por píxel (9,04 px/cm de la hoja del Tutor)
ESC_CABEZA_TUTOR = 0.000311   # m por píxel (36 px/cm en el primer plano)
ESC_PERRO = 0.0008            # m por píxel (perro de pie ≈ 0,67 m hasta las orejas)


def nuevo_archivo():
    bpy.ops.wm.read_homefile(use_empty=True)
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
    sc.render.engine = "BLENDER_EEVEE"
    return sc


def material(nombre, ruta, brillo=1.0):
    mat = bpy.data.materials.new(nombre)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    img = bpy.data.images.load(ruta)
    img.alpha_mode = "STRAIGHT"
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = img; tex.interpolation = "Linear"
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = brillo
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    nt.links.new(tex.outputs["Alpha"], mx.inputs["Fac"])
    nt.links.new(tr.outputs["BSDF"], mx.inputs[1])
    nt.links.new(em.outputs["Emission"], mx.inputs[2])
    nt.links.new(mx.outputs["Shader"], out.inputs["Surface"])
    return mat, img


def plano(nombre, ruta, x0, z0, ancho, alto, esc, y=0.0, padre=None, pos=(0, 0, 0), col=None, brillo=1.0):
    """Plano en XZ mirando a -Y. (x0, z0): esquina inferior izquierda respecto al origen del objeto, en píxeles
    (z hacia arriba). ancho/alto en píxeles."""
    mat, img = material(nombre, ruta, brillo)
    vs = [(x0 * esc, 0, z0 * esc), ((x0 + ancho) * esc, 0, z0 * esc),
          ((x0 + ancho) * esc, 0, (z0 + alto) * esc), (x0 * esc, 0, (z0 + alto) * esc)]
    me = bpy.data.meshes.new(nombre)
    me.from_pydata(vs, [], [(0, 1, 2, 3)])
    me.uv_layers.new(name="UV")
    uv = me.uv_layers[0].data
    for i, c in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
        uv[i].uv = c
    me.materials.append(mat)
    ob = bpy.data.objects.new(nombre, me)
    (col or bpy.context.scene.collection).objects.link(ob)
    ob.location = (pos[0], pos[1] + y, pos[2])
    ob.visible_shadow = False
    if padre:
        ob.parent = padre
    return ob


def sombra_contacto(nombre, ancho, fondo, opacidad, padre, col, z=0.004):
    mat = bpy.data.materials.new(nombre); mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1, 1, 1)
    gr = nt.nodes.new("ShaderNodeTexGradient"); gr.gradient_type = "SPHERICAL"
    cr = nt.nodes.new("ShaderNodeValToRGB")
    cr.color_ramp.elements[0].position = 0.0; cr.color_ramp.elements[0].color = (0, 0, 0, 1)
    cr.color_ramp.elements[1].position = 0.6; cr.color_ramp.elements[1].color = (1, 1, 1, 1)
    cr.color_ramp.interpolation = "EASE"
    mu = nt.nodes.new("ShaderNodeMath"); mu.operation = "MULTIPLY"; mu.inputs[1].default_value = opacidad
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (0, 0, 0, 1)
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    # coordenadas de objeto del plano van de -1 a 1; el degradado esférico es 1 en el centro y 0 a distancia 1
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], gr.inputs["Vector"])
    nt.links.new(gr.outputs["Fac"], cr.inputs["Fac"])
    nt.links.new(cr.outputs["Color"], mu.inputs[0])
    nt.links.new(mu.outputs["Value"], mx.inputs["Fac"])
    nt.links.new(tr.outputs["BSDF"], mx.inputs[1]); nt.links.new(em.outputs["Emission"], mx.inputs[2])
    nt.links.new(mx.outputs["Shader"], out.inputs["Surface"])
    me = bpy.data.meshes.new(nombre)
    me.from_pydata([(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)], [], [(0, 1, 2, 3)])
    me.materials.append(mat)
    ob = bpy.data.objects.new(nombre, me)
    col.objects.link(ob)
    ob.parent = padre; ob.location = (0, 0, z); ob.scale = (ancho / 2, fondo / 2, 1)
    ob.visible_shadow = False
    return ob


def raiz(nombre, col):
    e = bpy.data.objects.new(nombre, None)
    e.empty_display_type = "ARROWS"; e.empty_display_size = 0.15
    col.objects.link(e)
    return e


def conductor_visibilidad(ob, raiz_ob, prop, indice):
    for campo in ("hide_render", "hide_viewport"):
        fc = ob.driver_add(campo)
        d = fc.driver; d.type = "SCRIPTED"
        v = d.variables.new(); v.name = "v"; v.type = "SINGLE_PROP"
        v.targets[0].id = raiz_ob; v.targets[0].data_path = f'["{prop}"]'
        d.expression = f"v != {indice}"


def coleccion(nombre):
    c = bpy.data.collections.new(nombre)
    bpy.context.scene.collection.children.link(c)
    return c


def construir_tutor():
    nuevo_archivo()
    col = coleccion("PERSONAJE_tutor")
    P = R + "tutor\\piezas\\"
    man = json.load(open(RJ + "tutor/piezas/piezas.json"))
    r = raiz("tutor_sentado_frente", col)
    r["ojos"] = 0; r["boca"] = 0
    r["ojos_nombres"] = list(man["ojos"].keys()); r["boca_nombres"] = list(man["bocas"].keys())
    AX, AY = 310, 818           # base de la figura, en píxeles del recorte del cuerpo
    W, H = 620, 883
    s = ESC_CUERPO_TUTOR
    plano("tutor_cuerpo", P + "cuerpo_sentado_frente.png", -PAD - AX, -(H + PAD - AY), W + 2 * PAD, H + 2 * PAD, s, y=0.0, padre=r, col=col)
    # el centro de la base del cuello de la cabeza (435, 1000) cae sobre el cuello del cuerpo (332, 71) bajado 70 px
    cx, cy = 332, 71 + 25
    hs = ESC_CABEZA_TUTOR
    hx = (cx - AX) * s; hz = (AY - cy) * s
    HW, HH = 805, 1000
    plano("tutor_cabeza", P + "cabeza.png", -PAD_CABEZA - 435, -PAD_CABEZA, HW + 2 * PAD_CABEZA, HH + 2 * PAD_CABEZA, hs, y=0.004, padre=r, pos=(hx, 0, hz), col=col)
    for k, grupo, prop in (("ojos", man["ojos"], "ojos"), ("bocas", man["bocas"], "boca")):
        for i, (n, d) in enumerate(grupo.items()):
            x0, y0, x1, y1 = d["caja"]
            p = plano(f"tutor_{k}_{n}", P + d["archivo"].replace("/", "\\"), x0 - 435, HH - y1, x1 - x0, y1 - y0, hs, y=0.0025, padre=r, pos=(hx, 0, hz), col=col)
            conductor_visibilidad(p, r, prop, i)
    sombra_contacto("tutor_sombra_contacto", 0.95, 0.55, 0.6, r, col)
    return r


def construir_perro():
    nuevo_archivo()
    col = coleccion("PERSONAJE_perro")
    P = R + "perro\\piezas\\"
    ancl = {"sentado_frente": ((600, 944), (1317, 979)), "sentado_perfil": ((690, 950), (1317, 1017)),
            "de_pie_frente": ((613, 916), (1275, 969)), "de_pie_perfil": ((620, 868), (1275, 1017))}
    man = json.load(open(RJ + "perro/piezas/piezas.json"))
    s = ESC_PERRO
    raices = {}
    for n, ((ax, ay), (W, H)) in ancl.items():
        r = raiz(f"perro_{n}", col); raices[n] = r
        r["ojos"] = 0; r["ojos_nombres"] = ["abiertos", "cerrados"]
        plano(f"perro_cuerpo_{n}", P + f"cuerpo_{n}.png", -PAD - ax, -(H + PAD - ay), W + 2 * PAD, H + 2 * PAD, s, y=0.0, padre=r, col=col)
        frente = "frente" in n
        sombra_contacto(f"perro_sombra_contacto_{n}", 0.55 if frente else 0.95, 0.45 if frente else 0.5, 0.6, r, col)
        for k, d in man.items():
            if k.startswith("cuerpo") or not k.endswith(n):
                continue
            img = bpy.data.images.load(P + d["archivo"]); w, h = img.size
            ox, oy = d["origen"]
            if "pivote" in d:
                px, py = d["pivote"]
                plano(f"perro_{k}", P + d["archivo"], ox - px, -(oy + h - py), w, h, s, y=-0.002, padre=r,
                      pos=((px - ax) * s, 0, (ay - py) * s), col=col)
            else:   # parpadeo
                p = plano(f"perro_{k}", P + d["archivo"], ox - ax, -(oy + h - ay), w, h, s, y=-0.0025, padre=r, col=col)
                conductor_visibilidad(p, r, "ojos", 1)
    for i, r in enumerate(raices.values()):
        r.location = (i * 1.1, 0, 0)
    return raices
