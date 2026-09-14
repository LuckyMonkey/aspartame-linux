/*
 * Casilda Wayland Compositor Widget
 *
 * Copyright (C) 2024-2026  Juan Pablo Ugarte
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation;
 * version 2.1 of the License.
 *
 * library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
 *
 * Authors:
 *   Juan Pablo Ugarte <juanpablougarte@gmail.com>
 *
 * SPDX-License-Identifier: LGPL-2.1-only
 */

/**
 * CasildaCompositor:
 *
 * A simple Wayland compositor widget for Gtk 4.
 *
 * It was originally created for Cambalache's workspace using (wlroots)[https://gitlab.freedesktop.org/wlroots/wlroots],
 * a modular library to create Wayland compositors.
 *
 * Following Wayland tradition, this library is named after my hometown in Santa Fe, Argentina.
 *
 * To embed another process window in your Gtk 4 application all you have to do is create a CasildaCompositor widget
 * and add it in the hierarchy just like any other widget.
 *
 * You can specify which UNIX socket the compositor will listen for clients connections or use
 * [method@Casilda.Compositor.get_client_socket_fd] to get a already connected socket to the compositor.
 *
 * ```c
 * compositor = casilda_compositor_new ("/tmp/casilda-example.sock");
 * gtk_window_set_child (GTK_WINDOW (window), GTK_WIDGET (compositor));
 * ```
 *
 * Once the compositor is running you can connect to it by specifying the socket in WAYLAND_DISPLAY environment variable.
 *
 * ```bash
 * export GDK_BACKEND=wayland
 * export WAYLAND_DISPLAY=/tmp/casilda-example.sock
 * gtk4-demo
 * ```
 *
 * If you do not want any client being able to connect to the compositor you can pass NULL as socket and spawn the client
 * with [method@Casilda.Compositor.spawn_async] or get an already connected socket with
 * [method@Casilda.Compositor.get_client_socket_fd] and pass it to the client on WAYLAND_SOCKET env variable.
 *
 * ```c
 * compositor = casilda_compositor_new (NULL);
 * gtk_window_set_child (GTK_WINDOW (window), GTK_WIDGET (compositor));
 * gtk_window_present (GTK_WINDOW (window));
 *
 * gchar *argv[] = { "/usr/bin/gtk4-demo", NULL };
 * casilda_compositor_spawn_async (compositor, NULL, argv, NULL, G_SPAWN_DEFAULT, NULL, NULL, NULL, NULL);
 * ```
 *
 * Python example running gtk4-demo with [method@Casilda.Compositor.spawn_async]
 *
 * ```python
 * import gi
 * import sys
 *
 * gi.require_version("Gtk", "4.0")
 * gi.require_version("Casilda", "1.0")
 * from gi.repository import GLib, Gtk, Casilda
 *
 *
 * class CasildaApplication(Gtk.Application):
 *     def __init__(self):
 *         super().__init__(application_id="ar.xjuan.casilda.PyGObject.Example")
 *
 *     def do_activate(self):
 *         compositor = Casilda.Compositor()
 *
 *         window = Gtk.ApplicationWindow(
 *             application=self,
 *             title="Casilda Compositor",
 *             default_width=800,
 *             default_height=600,
 *             child=compositor
 *         )
 *
 *         compositor.spawn_async (
 *             None,
 *             ["/usr/bin/gtk4-demo"],
 *             None,
 *             GLib.SpawnFlags.DEFAULT
 *         )
 *
 *         window.present()
 *
 *
 * if __name__ == "__main__":
 *     app = CasildaApplication()
 *     sys.exit(app.run(sys.argv))
 * ```
 *
 * and the same in Javascript:
 *
 * ```javascript
 * import System from 'system';
 * import GLib from 'gi://GLib';
 * import GObject from 'gi://GObject';
 * import Gtk from 'gi://Gtk?version=4.0';
 * import Casilda from 'gi://Casilda?version=1.0';
 *
 *
 * let CasildaApplication = GObject.registerClass({},
 *     class CasildaApplication extends Gtk.Application {
 *     constructor() {
 *         super({
 *             application_id: 'ar.xjuan.casilda.Gjs.Example'
 *         });
 *     }
 *
 *     vfunc_activate() {
 *         let compositor = new Casilda.Compositor();
 *
 *         let window = new Gtk.ApplicationWindow({
 *             application: this,
 *             title: 'Casilda Compositor',
 *             default_width: 800,
 *             default_height: 600,
 *             child: compositor
 *         });
 *
 *         window.connect('close-request', () => {
 *             this.quit();
 *         });
 *
 *         compositor.spawn_async (
 *             null,
 *             ["/usr/bin/gtk4-demo"],
 *             null,
 *             GLib.SpawnFlags.DEFAULT,
 *             null
 *         );
 *
 *         window.present();
 *     }
 * });
 *
 * let app = new CasildaApplication();
 * app.run([System.programInvocationName].concat(ARGV));
 * ```
 */

#include "casilda-config.h"

#define _POSIX_C_SOURCE 200809L /* clock_gettime */
#define WLR_USE_UNSTABLE 1
#define G_LOG_DOMAIN "Casilda"
#define ENABLE_TEXTURE_DEBUG 0
#define ENABLE_BORDERS 0

#include <sys/socket.h>
#include <sys/un.h>
#include <linux/input-event-codes.h>
#include <wayland-server-core.h>
#include <wlr/backend.h>
#include <wlr/backend/interface.h>
#include <wlr/interfaces/wlr_keyboard.h>
#include <wlr/interfaces/wlr_output.h>
#include <wlr/interfaces/wlr_pointer.h>
#include <wlr/types/wlr_compositor.h>
#include <wlr/types/wlr_data_device.h>
#include <wlr/types/wlr_keyboard.h>
#include <wlr/types/wlr_output.h>
#include <wlr/types/wlr_output_layer.h>
#include <wlr/types/wlr_xdg_output_v1.h>
#include <wlr/types/wlr_pointer.h>
#include <wlr/types/wlr_pointer_gestures_v1.h>
#include <wlr/types/wlr_seat.h>
#include <wlr/types/wlr_subcompositor.h>
#include <wlr/types/wlr_xcursor_manager.h>
#include <wlr/types/wlr_xdg_activation_v1.h>
#include <wlr/types/wlr_cursor_shape_v1.h>
#include <wlr/types/wlr_xdg_shell.h>
#include <wlr/types/wlr_xdg_foreign_registry.h>
#include <wlr/types/wlr_xdg_foreign_v1.h>
#include <wlr/types/wlr_xdg_foreign_v2.h>
#include <wlr/types/wlr_viewporter.h>
#include <wlr/types/wlr_fractional_scale_v1.h>
#include <xkbcommon/xkbcommon.h>

#include <gtk/gtk.h>
#include <glib/gstdio.h>

#ifdef GDK_WINDOWING_WAYLAND
#include <gdk/wayland/gdkwayland.h>
#endif

#if defined(GDK_WINDOWING_X11) && defined(HAVE_X11_XCB)
#include <gdk/x11/gdkx.h>
#include <X11/Xlib-xcb.h>
#include <xkbcommon/xkbcommon-x11.h>
#endif

#include "casilda.h"
#include "casilda-private.h"
#include "casilda-wayland-source.h"

typedef enum {
  CASILDA_POINTER_MODE_FOWARD,
  CASILDA_POINTER_MODE_RESIZE,
  CASILDA_POINTER_MODE_MOVE,
} CasildaPointerMode;

typedef struct CasildaCompositorToplevel CasildaCompositorToplevel;
typedef struct CasildaCompositorPopup CasildaCompositorPopup;

typedef struct
{
  GtkWidget *self;

  /* wayland main loop integration */
  GSource *wl_source;

  /* Event controllers */
  GtkEventController *motion_controller;
  GtkEventController *scroll_controller;
  GtkEventController *touchpad_gesture_controller;
  GtkEventController *key_controller;
  GtkGesture         *click_gesture;
  GdkDevice          *gkeyboard;
  GdkDevice          *gpointer;

  /* Frame Clock state */
  GdkFrameClock                  *frame_clock;
  gboolean                        frame_clock_updating;
  gulong                          frame_clock_source;
  guint                           defered_present_event_source;
  struct wlr_output_event_present defered_present_event;

  /* Renderer context */
  GdkGLContext *gl_context;

  GdkClipboard *clipboard;
  gulong        clipboard_source;
  GdkContentProvider *clipboard_provider;

  /* Wayland display */
  struct wl_display *wl_display;

  /* Custom wlr objects */
  struct wlr_keyboard keyboard;
  struct wlr_pointer  pointer;
  struct wlr_backend  backend;
  struct wlr_output   output;
  struct wl_listener  output_bind;

  /* Extra input */
  struct wlr_pointer_gestures_v1 *pointer_gestures;

  /* wlr interfaces */
  struct wlr_backend_impl backend_impl;
  struct wlr_output_impl  output_impl;

  /* XDG shell */
  struct wl_listener    new_xdg_toplevel;
  struct wl_listener    new_xdg_popup;
  GList                *toplevels;

  /* XDG activation */
  struct wl_listener    request_activate;

  /* cursor-shape-v1 protocol */
  struct wl_listener    request_set_shape;

  GHashTable            *toplevel_state;

  /* Widget logical coordinates in root surface */
  GdkSurface *root_surface;
  gdouble surface_origin_x, surface_origin_y;
  gdouble scale;

  /* Toplevel resize state */
  gdouble                    pointer_x, pointer_y; /* Current pointer position */
  CasildaCompositorToplevel *grabbed_toplevel;
  CasildaPointerMode         pointer_mode;
  gdouble                    grab_x, grab_y;
  struct wlr_box             grab_box;
  uint32_t                   resize_edges;

  /* Virtual Seat */
  struct wlr_seat   *seat;
  struct wl_listener request_cursor;
  struct wl_listener request_set_selection;

  struct wl_listener on_request_cursor;
  struct wl_listener on_cursor_surface_commit;
  struct wl_listener on_cursor_surface_destroy;
  gint               hotspot_x;
  gint               hotspot_y;
  GdkTexture        *cursor_gdk_texture;
  GdkCursor         *cursor_gdk_cursor;

  /* xdg_foreign */
  struct wlr_xdg_foreign_registry *foreign_registry;

  /* Drag & Drop */
  GdkDrag            *drag;
  GtkDropTargetAsync *drop_target;
  GdkContentProvider *drag_provider;

  struct wl_listener request_start_drag;
  struct wl_listener on_drag_icon_surface_commit;
  struct wl_listener on_drag_icon_surface_destroy;
  GdkTexture        *drag_icon_texture;

  /* Event controller state */
  gboolean          scroll_begun;

  /* GObject properties */
  gchar       *socket;

  GtkAdjustment *adjustment[2];
} CasildaCompositorPrivate;


struct _CasildaCompositor
{
  GtkWidget parent;
};


typedef struct
{
  gboolean maximized, fullscreen;
  gint     x, y, width, height;
} CasildaCompositorToplevelState;


typedef struct
{
  struct wl_listener new_subsurface;
  GList *list;
} CasildaCompositorSurfaces;


struct CasildaCompositorToplevel
{
  CasildaCompositorPrivate *priv;
  struct wlr_xdg_toplevel  *xdg_toplevel;

  GList *toplevels;
  GList *popups;

  CasildaCompositorSurfaces subsurfaces;
  gboolean needs_update;

  gint x;
  gint y;

  struct wlr_box last_commit_geometry;

  CasildaCompositorToplevelState old_state;

  /* This points to priv->toplevel_state[app_id] */
  CasildaCompositorToplevelState *state;

  /* Events */
  struct wl_listener map;
  struct wl_listener unmap;
  struct wl_listener commit;
  struct wl_listener destroy;
  struct wl_listener request_move;
  struct wl_listener request_resize;
  struct wl_listener request_maximize;
  struct wl_listener request_fullscreen;
  struct wl_listener set_app_id;
};

struct CasildaCompositorPopup
{
  CasildaCompositorPrivate  *priv;

  CasildaCompositorToplevel *toplevel;
  CasildaCompositorPopup    *parent;

  struct wlr_xdg_popup *xdg_popup;

  CasildaCompositorSurfaces subsurfaces;
  GList *popups;

  struct wl_listener    commit;
  struct wl_listener    destroy;
};

typedef struct
{
  CasildaCompositorPrivate  *priv;
  CasildaCompositorSurfaces *parent;

  struct wlr_subsurface     *wlr_subsurface;

  struct wl_listener    commit;
  struct wl_listener    destroy;
} CasildaCompositorSubsurface;


enum {
  PROP_0,
  PROP_SOCKET,

  N_PROPERTIES,

  PROP_HADJUSTMENT,
  PROP_VADJUSTMENT,
  PROP_HSCROLL_POLICY,
  PROP_VSCROLL_POLICY
};

static GParamSpec *properties[N_PROPERTIES];

G_DEFINE_TYPE_WITH_CODE (CasildaCompositor, casilda_compositor, GTK_TYPE_WIDGET,
                         G_ADD_PRIVATE (CasildaCompositor)
                         G_IMPLEMENT_INTERFACE (GTK_TYPE_SCROLLABLE, NULL))
#define GET_PRIVATE(d) ((CasildaCompositorPrivate *) casilda_compositor_get_instance_private ((CasildaCompositor *) d))


static void casilda_compositor_wlr_init (CasildaCompositorPrivate *priv);
static void casilda_compositor_toplevel_configure (CasildaCompositorToplevel *toplevel,
                                                   gint                       x,
                                                   gint                       y,
                                                   gint                       width,
                                                   gint                       height);

static gboolean
xdg_surface_get_data (struct wlr_xdg_surface *xdg_surface, struct wlr_surface **surface, struct wlr_box *geometry)
{
  if (!xdg_surface || !(*surface = xdg_surface->surface))
    return TRUE;

  if (geometry)
    *geometry = xdg_surface->geometry;

  return FALSE;
}

static void
casilda_compositor_get_scroll_offset (CasildaCompositorPrivate *priv, gint *x, gint *y)
{
  if (priv->adjustment[GTK_ORIENTATION_HORIZONTAL])
    *x = gtk_adjustment_get_value (priv->adjustment[GTK_ORIENTATION_HORIZONTAL]);
  else
    *x = 0;

  if (priv->adjustment[GTK_ORIENTATION_VERTICAL])
    *y = gtk_adjustment_get_value (priv->adjustment[GTK_ORIENTATION_VERTICAL]);
  else
    *y = 0;
}

#if ENABLE_BORDERS
static void
debug_snapshot_border (CasildaCompositorPrivate *priv,
                       GtkSnapshot *snapshot,
                       gint x, gint y, gint w, gint h,
                       gfloat r, gfloat g, gfloat b)
{
  gint offset_x, offset_y;

  casilda_compositor_get_scroll_offset (priv, &offset_x, &offset_y);

#define COLOR { r, g, b, 1 }
  gtk_snapshot_append_border (snapshot,
                              &GSK_ROUNDED_RECT_INIT (x-offset_x, y-offset_y, w, h),
                              (float[4]) { 1, 1, 1, 1 },
                              (GdkRGBA[4]) { COLOR, COLOR, COLOR, COLOR });
#undef COLOR
}

static void
debug_snapshot_toplevel_border (GtkSnapshot *snapshot,
                                CasildaCompositorToplevel *toplevel,
                                gfloat r, gfloat g, gfloat b)
{
  struct wlr_surface *surface;
  struct wlr_box tbox = {0, };

  if (!toplevel->xdg_toplevel || xdg_surface_get_data (toplevel->xdg_toplevel->base, &surface, &tbox))
    return;

  GdkTexture *texture = surface->data;

  if (texture)
    debug_snapshot_border (toplevel->priv,
                           snapshot,
                           toplevel->x - tbox.x,
                           toplevel->y - tbox.y,
                           gdk_texture_get_width (texture),
                           gdk_texture_get_height (texture),
                           r, g, b);
}

#else
#define debug_snapshot_border(p,s,x,y,w,h,r,g,b)
#define debug_snapshot_toplevel_border(s,t,r,g,b)
#endif


#if ENABLE_TEXTURE_DEBUG
static gint texture_count = 0;

static void
texture_weak_ref_callback (G_GNUC_UNUSED gpointer data, GObject* object)
{
  texture_count--;
  g_message ("%s object=%p texture_count=%d", __func__, object, texture_count);
}

static void
texture_debug_add_weak (gpointer object)
{
  g_object_weak_ref (G_OBJECT (object), texture_weak_ref_callback, NULL);
  texture_count++;

  g_message ("%s object=%p texture_count=%d", __func__, object, texture_count);
}

#else
#define texture_debug_add_weak(o)
#endif

typedef struct {
  CasildaCompositorPrivate *priv;
  GtkSnapshot *snapshot;
  struct timespec now;
  gint scroll_offset_x;
  gint scroll_offset_y;
  gint parent_x;
  gint parent_y;
} SnapshotData;

static void
snapshot_surfaces (struct wlr_surface *surface, int sx, int sy, void *data)
{
  SnapshotData *sdata = data;
  CasildaCompositorPrivate *priv = sdata->priv;
  GdkTexture *texture = surface->data;
  gfloat scale = priv->scale;

  if (!texture)
    {
      g_debug ("No texture for wlr_surface %p", surface);
      goto frame;
    }

  texture_debug_add_weak (texture);

  gint w = gdk_texture_get_width (texture);
  gint h = gdk_texture_get_height (texture);

  gtk_snapshot_save (sdata->snapshot);

  /* Calculate subsurface origin with parent surface coordinates and scroll offset */
  gfloat x = (sdata->parent_x + sx) - sdata->scroll_offset_x;
  gfloat y = (sdata->parent_y + sy) - sdata->scroll_offset_y;

  /* Snap logical coordinates to device pixel grid */
  if (scale > 1.0)
    {
      x = floorf ((x + priv->surface_origin_x) * scale) / scale - priv->surface_origin_x;
      y = floorf ((y + priv->surface_origin_y) * scale) / scale - priv->surface_origin_y;
    }

  gtk_snapshot_translate (sdata->snapshot, &GRAPHENE_POINT_INIT (x, y));

  if (surface->current.viewport.has_dst)
    {
      w = surface->current.viewport.dst_width;
      h = surface->current.viewport.dst_height;
    }
  else if (surface->current.scale > 1)
    {
      w /= surface->current.scale;
      h /= surface->current.scale;
    }

  switch (surface->current.transform)
    {
    case WL_OUTPUT_TRANSFORM_90:
    case WL_OUTPUT_TRANSFORM_FLIPPED_90:
      gtk_snapshot_translate (sdata->snapshot, &GRAPHENE_POINT_INIT (h, 0));
      gtk_snapshot_rotate (sdata->snapshot, 90);
      break;
    case WL_OUTPUT_TRANSFORM_180:
    case WL_OUTPUT_TRANSFORM_FLIPPED_180:
      gtk_snapshot_translate (sdata->snapshot, &GRAPHENE_POINT_INIT (w, h));
      gtk_snapshot_rotate (sdata->snapshot, 180);
      break;
    case WL_OUTPUT_TRANSFORM_270:
    case WL_OUTPUT_TRANSFORM_FLIPPED_270:
      gtk_snapshot_translate (sdata->snapshot, &GRAPHENE_POINT_INIT (0, w));
      gtk_snapshot_rotate (sdata->snapshot, 270);
      break;
    default:
      break;
    }

  if (surface->current.transform >= WL_OUTPUT_TRANSFORM_FLIPPED)
    {
      gtk_snapshot_scale (sdata->snapshot, -1.0, 1.0);
      gtk_snapshot_translate (sdata->snapshot, &GRAPHENE_POINT_INIT (-w, 0));
    }

  if (surface->current.viewport.has_src)
    {
      struct wlr_fbox *src = &surface->current.viewport.src;
      /* FIXME: this was never tested since Gtk clients do no seems to use it */
      gtk_snapshot_push_clip (sdata->snapshot, &GRAPHENE_RECT_INIT (src->x, src->y, src->width, src->height));
    }

  gdk_paintable_snapshot (GDK_PAINTABLE (texture), sdata->snapshot, w, h);

  if (surface->current.viewport.has_src)
    gtk_snapshot_pop (sdata->snapshot);

  gtk_snapshot_restore (sdata->snapshot);

frame:
  wlr_surface_send_frame_done (surface, &sdata->now);
}

static void
snapshot_surface (struct wlr_surface *surface, SnapshotData *data, gint x, gint y)
{
  data->parent_x = x;
  data->parent_y = y;
  wlr_surface_for_each_surface (surface, snapshot_surfaces, data);
}

static void
casilda_compositor_snapshot_popup (CasildaCompositorPopup *popup, SnapshotData *data, gint parent_x, gint parent_y)
{
  struct wlr_surface *psurface;
  struct wlr_box pbox = {0, };

  if (!popup->xdg_popup || xdg_surface_get_data (popup->xdg_popup->base, &psurface, &pbox))
    return;

  gint popup_x = parent_x + popup->xdg_popup->current.geometry.x;
  gint popup_y = parent_y + popup->xdg_popup->current.geometry.y;

  snapshot_surface (psurface, data, popup_x - pbox.x, popup_y - pbox.y);

  for (GList *l = popup->popups; l; l = g_list_next (l))
    casilda_compositor_snapshot_popup (l->data, data, popup_x, popup_y);
}


static void
casilda_compositor_snapshot_toplevel (CasildaCompositorToplevel *toplevel, SnapshotData *data)
{
  struct wlr_surface *surface;
  struct wlr_box tbox = {0, };

  if (!toplevel->xdg_toplevel || xdg_surface_get_data (toplevel->xdg_toplevel->base, &surface, &tbox))
    return;

  gboolean has_transient = toplevel->toplevels != NULL;

  if (has_transient)
    {
      graphene_matrix_t matrix;
      graphene_vec4_t offset;

      graphene_matrix_init_from_float (&matrix,
                                       (float[16]) {
                                                     0.8, 0, 0, 0,
                                                     0, 0.8, 0, 0,
                                                     0, 0, 0.8, 0,
                                                     0, 0, 0, 1
                                                   });

      graphene_vec4_init (&offset, 0, 0, 0, 0);
      gtk_snapshot_push_color_matrix (data->snapshot, &matrix, &offset);
    }

  debug_snapshot_toplevel_border (data->snapshot, toplevel, 1, 0, 0);

  snapshot_surface (surface, data, toplevel->x - tbox.x, toplevel->y - tbox.y);

  /* Recurse toplevel popups */
  for (GList *l = toplevel->popups; l; l = g_list_next (l))
    casilda_compositor_snapshot_popup (l->data, data, toplevel->x, toplevel->y);

  if (has_transient)
    gtk_snapshot_pop (data->snapshot);

  /* Recurse toplevel transient windows */
  for (GList *l = toplevel->toplevels; l; l = g_list_next (l))
    casilda_compositor_snapshot_toplevel (l->data, data);
}

static inline gboolean
casilda_compositor_is_scrollable (CasildaCompositorPrivate *priv)
{
  return priv->adjustment[GTK_ORIENTATION_HORIZONTAL] && priv->adjustment[GTK_ORIENTATION_VERTICAL];
}

static void
casilda_compositor_set_output_resolution (CasildaCompositorPrivate *priv, gint output_width, gint output_height)
{
  struct wlr_output_state state;

  wlr_output_state_init (&state);
  wlr_output_state_set_enabled (&state, true);
  wlr_output_state_set_custom_mode (&state, output_width * priv->scale, output_height * priv->scale, 0);
  wlr_output_state_set_scale (&state, priv->scale);
  wlr_output_commit_state (&priv->output, &state);
  wlr_output_state_finish (&state);
}

static void
surface_notify_scale (struct wlr_surface *surface, gfloat scale)
{
  if (scale < 1.0f)
    scale = 1.0f;

  wlr_fractional_scale_v1_notify_scale (surface, scale);
  wlr_surface_set_preferred_buffer_scale (surface, ceil (scale));
}

static void
casilda_compositor_toplevel_notify_scale (CasildaCompositorPrivate *priv, CasildaCompositorToplevel *toplevel)
{
  surface_notify_scale (toplevel->xdg_toplevel->base->surface, priv->scale);

  for (GList *l = toplevel->toplevels; l; l = g_list_next (l))
    casilda_compositor_toplevel_notify_scale (priv, l->data);

  for (GList *l = toplevel->popups; l; l = g_list_next (l))
    {
      CasildaCompositorPopup *popup = l->data;
      surface_notify_scale (popup->xdg_popup->base->surface, priv->scale);
    }
}

static void
on_root_surface_notify (GObject *object, G_GNUC_UNUSED GParamSpec *spec, GtkWidget *compositor)
{
  CasildaCompositorPrivate *priv = GET_PRIVATE (compositor);
  GdkSurface *surface = GDK_SURFACE (object);

  priv->scale = gdk_surface_get_scale (surface);

  casilda_compositor_set_output_resolution (priv, gtk_widget_get_width (compositor), gtk_widget_get_height (compositor));

  /* Update scale */
  for (GList *l = priv->toplevels; l; l = g_list_next (l))
    casilda_compositor_toplevel_notify_scale (priv, l->data);

}

static void
casilda_compositor_update_native_data (CasildaCompositorPrivate *priv)
{
  GtkRoot *root = gtk_widget_get_root (priv->self);
  graphene_point_t out_point;
  GdkSurface *surface;

  if (!root)
    return;

  surface = gtk_native_get_surface (GTK_NATIVE (root));

  if (priv->root_surface != surface)
    {
      if (priv->root_surface)
        g_signal_handlers_disconnect_by_func (priv->root_surface, on_root_surface_notify, priv->self);

      priv->root_surface = surface;

      g_signal_connect_object (surface, "notify::scale", G_CALLBACK (on_root_surface_notify), priv->self, G_CONNECT_DEFAULT);
    }

  /* Get scale */
  priv->scale = gdk_surface_get_scale (surface);

  /* Get native surface transform */
  gtk_native_get_surface_transform (GTK_NATIVE (root), &priv->surface_origin_x, &priv->surface_origin_y);

  /* Add widget offset */
  if (gtk_widget_compute_point (priv->self, GTK_WIDGET (root), &GRAPHENE_POINT_INIT (0, 0), &out_point))
    {
      priv->surface_origin_x += out_point.x;
      priv->surface_origin_y += out_point.y;
    }
}

static void
casilda_compositor_snapshot (GtkWidget *widget, GtkSnapshot *snapshot)
{
  CasildaCompositorPrivate *priv = GET_PRIVATE (widget);
  SnapshotData data = { priv, snapshot, {0, }, 0, 0, 0, 0 };

  clock_gettime (CLOCK_MONOTONIC, &data.now);

  /* Get scrollable offset */
  casilda_compositor_get_scroll_offset (priv, &data.scroll_offset_x, &data.scroll_offset_y);

  /* Iterate all toplevels */
  for (GList *l = g_list_last (priv->toplevels); l; l = g_list_previous (l))
    casilda_compositor_snapshot_toplevel (l->data, &data);

  if (priv->frame_clock_updating)
    {
      if (priv->frame_clock)
        gdk_frame_clock_end_updating (priv->frame_clock);

      priv->frame_clock_updating = FALSE;
    }
}

static void
casilda_compositor_queue_draw (CasildaCompositorPrivate *priv)
{
  if (priv->frame_clock && !priv->frame_clock_updating)
    {
      priv->frame_clock_updating = TRUE;
      gdk_frame_clock_begin_updating (priv->frame_clock);
    }

  gtk_widget_queue_draw (priv->self);
}

static void
compositor_calculate_virtual_size (CasildaCompositorPrivate *priv, GList *toplevels, gint *width, gint *height)
{
  for (GList *l = toplevels; l; l = g_list_next (l))
    {
      CasildaCompositorToplevel *toplevel = l->data;
      struct wlr_box *tbox = NULL;

      if (!toplevel->xdg_toplevel)
        continue;

      tbox = &toplevel->xdg_toplevel->base->geometry;

      gint w = toplevel->x + tbox->width;
      gint h = toplevel->y + tbox->height;

      if (w > *width)
        *width = w;

      if (h > *height)
        *height = h;

      if (toplevel->toplevels)
        compositor_calculate_virtual_size (priv, toplevel->toplevels, width, height);
    }
}

static void
compositor_update_scrollable_adjustment (CasildaCompositorPrivate *priv)
{
  if (!casilda_compositor_is_scrollable (priv))
    return;

  gint w = gtk_widget_get_width (priv->self);
  gint h = gtk_widget_get_height (priv->self);

  gtk_adjustment_set_page_size (priv->adjustment[GTK_ORIENTATION_HORIZONTAL], w);
  gtk_adjustment_set_page_size (priv->adjustment[GTK_ORIENTATION_VERTICAL], h);

  compositor_calculate_virtual_size (priv, priv->toplevels, &w, &h);

  gtk_adjustment_set_upper (priv->adjustment[GTK_ORIENTATION_HORIZONTAL], w);
  gtk_adjustment_set_upper (priv->adjustment[GTK_ORIENTATION_VERTICAL], h);
}

static void
casilda_compositor_size_allocate (GtkWidget *widget, int w, int h, G_GNUC_UNUSED int b)
{
  CasildaCompositorPrivate *priv = GET_PRIVATE (widget);
  gint output_width = w, output_height = h;

  /* Update scale and compositor origin in root surface */
  casilda_compositor_update_native_data (priv);

  if (casilda_compositor_is_scrollable (priv))
    {
      /* Update scrollable values */
      compositor_update_scrollable_adjustment (priv);

      output_width = gtk_adjustment_get_upper (priv->adjustment[GTK_ORIENTATION_HORIZONTAL]);
      output_height = gtk_adjustment_get_upper (priv->adjustment[GTK_ORIENTATION_VERTICAL]);
    }

  casilda_compositor_set_output_resolution (priv, output_width, output_height);

  /* Resize maximized/fullscreen windows */
  for (GList *l = priv->toplevels; l; l = g_list_next (l))
    {
      CasildaCompositorToplevel *toplevel = l->data;

      if (toplevel->xdg_toplevel->current.maximized || toplevel->xdg_toplevel->current.fullscreen)
        casilda_compositor_toplevel_configure (toplevel, 0, 0, w, h);
    }
}

static void
listener_clear (struct wl_listener *listener)
{
  if (listener && listener->notify)
    {
      wl_list_remove (&listener->link);
      memset (listener, 0, sizeof (struct wl_listener));
    }
}

static void
casilda_compositor_cursor_handler_remove (CasildaCompositorPrivate *priv)
{
  listener_clear (&priv->on_cursor_surface_commit);
  listener_clear (&priv->on_cursor_surface_destroy);
}

static void
casilda_compositor_reset_cursor (CasildaCompositorPrivate *priv)
{
  if (priv->self)
    gtk_widget_set_cursor (priv->self, NULL);

  g_clear_object (&priv->cursor_gdk_cursor);
  g_clear_object (&priv->cursor_gdk_texture);
}

static void
casilda_compositor_reset_pointer_mode (CasildaCompositorPrivate *priv)
{
  priv->pointer_mode = CASILDA_POINTER_MODE_FOWARD;
  priv->grabbed_toplevel = NULL;
}

static void
casilda_compositor_reset_drag_icon (CasildaCompositorPrivate *priv)
{
  g_clear_object (&priv->drag_icon_texture);
  listener_clear (&priv->on_drag_icon_surface_commit);
  listener_clear (&priv->on_drag_icon_surface_destroy);
}

static CasildaCompositorToplevel *
get_toplevel_from_popup_at_pointer (CasildaCompositorToplevel *toplevel,
                                    CasildaCompositorPopup    *popup,
                                    gint                       parent_x,
                                    gint                       parent_y,
                                    struct wlr_surface       **surface,
                                    double                    *sx,
                                    double                    *sy)
{
  CasildaCompositorPrivate *priv = toplevel->priv;
  struct wlr_xdg_surface *xdg_surface;

  if (!popup->xdg_popup || !(xdg_surface = popup->xdg_popup->base))
    return NULL;

  struct wlr_box geo = xdg_surface->geometry;

  gint popup_x = parent_x + popup->xdg_popup->current.geometry.x;
  gint popup_y = parent_y + popup->xdg_popup->current.geometry.y;

  for (GList *pl = g_list_last (popup->popups); pl; pl = g_list_previous (pl))
    {
      CasildaCompositorToplevel *t;
      if ((t = get_toplevel_from_popup_at_pointer (toplevel, pl->data, popup_x, popup_y, surface, sx, sy)))
        return toplevel;
    }

  double psx = priv->pointer_x - popup_x + geo.x;
  double psy = priv->pointer_y - popup_y + geo.y;

  struct wlr_surface *s = wlr_surface_surface_at (xdg_surface->surface, psx, psy, sx, sy);

  if (s)
    {
      if (surface)
        *surface = s;

      return toplevel;
    }

  return NULL;
}

static CasildaCompositorToplevel *
get_toplevel_at_pointer (CasildaCompositorToplevel *toplevel,
                         struct wlr_surface       **surface,
                         double                    *sx,
                         double                    *sy)
{
  CasildaCompositorPrivate *priv = toplevel->priv;
  struct wlr_xdg_surface *xdg_surface;

  if (!toplevel->xdg_toplevel || !(xdg_surface = toplevel->xdg_toplevel->base))
    return NULL;

  /* Recurse toplevels first */
  for (GList *l = toplevel->toplevels; l; l = g_list_next (l))
    {
      CasildaCompositorToplevel *toplevel = get_toplevel_at_pointer (l->data, surface, sx, sy);
      if (toplevel)
        return toplevel;
    }

  /* Then iterate popups */
  for (GList *pl = g_list_last (toplevel->popups); pl; pl = g_list_previous (pl))
    {
      CasildaCompositorToplevel *t;
      if ((t = get_toplevel_from_popup_at_pointer (toplevel, pl->data, toplevel->x, toplevel->y, surface, sx, sy)))
        return toplevel;
    }

  struct wlr_box box = xdg_surface->geometry;
  double tsx = priv->pointer_x - toplevel->x + box.x;
  double tsy = priv->pointer_y - toplevel->y + box.y;

  struct wlr_surface *s = wlr_surface_surface_at (xdg_surface->surface, tsx, tsy, sx, sy);

  if (s)
    {
      if (surface)
        *surface = s;

      return toplevel;
    }

  return NULL;
}

static CasildaCompositorToplevel *
casilda_compositor_get_toplevel_at_pointer (CasildaCompositorPrivate *priv,
                                            struct wlr_surface      **surface,
                                            double                   *sx,
                                            double                   *sy)
{
  if (surface)
    *surface = NULL;

  for (GList *l = priv->toplevels; l; l = g_list_next (l))
    {
      CasildaCompositorToplevel *toplevel = get_toplevel_at_pointer (l->data, surface, sx, sy);
      if (toplevel)
        return toplevel;
    }

  return NULL;
}

static void
casilda_compositor_toplevel_set_position (CasildaCompositorToplevel *toplevel, gint x, gint y)
{
  toplevel->x = x;
  toplevel->y = y;

  casilda_compositor_queue_draw (toplevel->priv);

  compositor_update_scrollable_adjustment (toplevel->priv);
}

static void
casilda_compositor_toplevel_configure (CasildaCompositorToplevel *toplevel,
                                       gint                       x,
                                       gint                       y,
                                       gint                       width,
                                       gint                       height)
{
  casilda_compositor_toplevel_set_position (toplevel, x, y);

  if (width && height)
    {
      toplevel->xdg_toplevel->scheduled.width = width;
      toplevel->xdg_toplevel->scheduled.height = height;
      wlr_xdg_surface_schedule_configure (toplevel->xdg_toplevel->base);
    }
}

static void
casilda_compositor_toplevel_save_position (CasildaCompositorToplevel *toplevel)
{
  CasildaCompositorToplevelState *state = toplevel->state;

  if (!state)
    return;

  /* Get position from scene node */
  state->x = toplevel->x;
  state->y = toplevel->y;

  g_debug ("%s %s %dx%d %dx%d maximized=%d fullscreen=%d",
           __func__,
           toplevel->xdg_toplevel->app_id,
           state->x,
           state->y,
           state->width,
           state->height,
           state->maximized,
           state->fullscreen);
}

static void
casilda_compositor_toplevel_save_size (CasildaCompositorToplevel *toplevel,
                                       gint                       width,
                                       gint                       height)
{
  CasildaCompositorToplevelState *state = toplevel->state;

  if (!state)
    return;

  /* Assign current state from toplevel */
  state->width = width;
  state->height = height;

  g_debug ("%s %s %dx%d %dx%d maximized=%d fullscreen=%d",
           __func__,
           toplevel->xdg_toplevel->app_id,
           state->x,
           state->y,
           state->width,
           state->height,
           state->maximized,
           state->fullscreen);
}

static void
casilda_compositor_toplevel_save_state (CasildaCompositorToplevel *toplevel)
{
  struct wlr_xdg_toplevel *xdg_toplevel = toplevel->xdg_toplevel;
  struct wlr_box geometry = xdg_toplevel->base->geometry;

  toplevel->old_state.x = toplevel->x;
  toplevel->old_state.y = toplevel->y;
  toplevel->old_state.width = geometry.width;
  toplevel->old_state.height = geometry.height;
}

static void
casilda_compositor_toplevel_toggle_maximize_fullscreen (CasildaCompositorToplevel *toplevel,
                                                        gboolean                   fullscreen)
{
  CasildaCompositorPrivate *priv = toplevel->priv;
  struct wlr_xdg_toplevel *xdg_toplevel = toplevel->xdg_toplevel;
  CasildaCompositorToplevelState *state = toplevel->state;
  gboolean value;

  if (!xdg_toplevel->base->initialized || !xdg_toplevel->base->configured)
    return;

  if (fullscreen)
    {
      value = xdg_toplevel->requested.fullscreen;
      if (xdg_toplevel->current.fullscreen == value)
        return;

      xdg_toplevel->scheduled.fullscreen = value;

      if (state)
        state->fullscreen = value;
    }
  else
    {
      value = xdg_toplevel->requested.maximized;
      if (xdg_toplevel->current.maximized == value)
        return;

      xdg_toplevel->scheduled.maximized = value;

      if (state)
        state->maximized = value;
    }

  if (value)
    {
      GtkWidget *widget = priv->self;
      casilda_compositor_toplevel_save_state (toplevel);
      casilda_compositor_toplevel_configure (toplevel,
                                             0, 0,
                                             gtk_widget_get_width (widget),
                                             gtk_widget_get_height (widget));
    }
  else
    {
      casilda_compositor_toplevel_configure (toplevel,
                                             toplevel->old_state.x,
                                             toplevel->old_state.y,
                                             toplevel->old_state.width,
                                             toplevel->old_state.height);
    }
}

static void
casilda_compositor_handle_pointer_resize_toplevel (CasildaCompositorPrivate *priv)
{
  CasildaCompositorToplevel *toplevel = priv->grabbed_toplevel;
  struct wlr_xdg_toplevel *xdg_toplevel = toplevel->xdg_toplevel;
  struct wlr_box box;
  gint border_x = priv->pointer_x - priv->grab_x;
  gint border_y = priv->pointer_y - priv->grab_y;
  gint new_left = priv->grab_box.x;
  gint new_right = priv->grab_box.x + priv->grab_box.width;
  gint new_top = priv->grab_box.y;
  gint new_bottom = priv->grab_box.y + priv->grab_box.height;
  gint new_width, new_height, min_width, min_height;

  min_width = xdg_toplevel->current.min_width;
  min_height = xdg_toplevel->current.min_height;

  if (priv->resize_edges & WLR_EDGE_TOP)
    {
      new_top = border_y;
      if (new_top >= new_bottom)
        new_top = new_bottom - 1;
    }
  else if (priv->resize_edges & WLR_EDGE_BOTTOM)
    {
      new_bottom = border_y;
      if (new_bottom <= new_top)
        new_bottom = new_top + 1;
    }

  if (priv->resize_edges & WLR_EDGE_LEFT)
    {
      new_left = border_x;
      if (new_left >= new_right)
        new_left = new_right - 1;
    }
  else if (priv->resize_edges & WLR_EDGE_RIGHT)
    {
      new_right = border_x;
      if (new_right <= new_left)
        new_right = new_left + 1;
    }

  new_width = new_right - new_left;
  new_height = new_bottom - new_top;

  if (new_width < min_width && new_height < min_height)
    return;

  if (new_width < min_width)
    {
      if (priv->resize_edges & WLR_EDGE_LEFT)
        new_left -= min_width - new_width;
      new_width = min_width;
    }

  if (new_height < min_height)
    {
      if (priv->resize_edges & WLR_EDGE_TOP)
        new_top -= min_height - new_height;
      new_height = min_height;
    }

  box = toplevel->xdg_toplevel->base->geometry;

  wlr_xdg_toplevel_set_size (toplevel->xdg_toplevel, new_width, new_height);

  /* FIXME: we probably need to wait for the new size to be in effect
   * before setting the position
   */
  casilda_compositor_toplevel_set_position (toplevel, new_left - box.x, new_top - box.y);

  casilda_compositor_toplevel_save_position (toplevel);
  casilda_compositor_toplevel_save_size (toplevel, new_width, new_height);
}

static void
casilda_compositor_handle_pointer_motion (CasildaCompositorPrivate *priv, gdouble x, gdouble y)
{
  gint x_offset, y_offset;

  casilda_compositor_get_scroll_offset (priv, &x_offset, &y_offset);

  /* Clamp pointer to widget coordinates */
  x = CLAMP (x, 0, gtk_widget_get_width (priv->self));
  y = CLAMP (y, 0, gtk_widget_get_height (priv->self));

  /* Add scrollable offset */
  priv->pointer_x = x + x_offset;
  priv->pointer_y = y + y_offset;

  if (priv->grabbed_toplevel && priv->pointer_mode == CASILDA_POINTER_MODE_MOVE)
    {
      /* Unmaximize maximized windows on move */
      if (priv->grabbed_toplevel && priv->grabbed_toplevel->xdg_toplevel->current.maximized)
        {
          struct wlr_box geometry = priv->grabbed_toplevel->xdg_toplevel->base->geometry;
          gfloat ratio = priv->grab_x / (gfloat)geometry.width;

          /* Adjust grab position */
          priv->grab_x = priv->grabbed_toplevel->old_state.width * ratio;

          priv->grabbed_toplevel->old_state.x = priv->pointer_x - priv->grab_x;
          priv->grabbed_toplevel->old_state.y = priv->pointer_y - priv->grab_y;
          priv->grabbed_toplevel->xdg_toplevel->requested.maximized = FALSE;
          casilda_compositor_toplevel_toggle_maximize_fullscreen (priv->grabbed_toplevel, FALSE);
          return;
        }

      casilda_compositor_toplevel_set_position (priv->grabbed_toplevel,
                                                priv->pointer_x - priv->grab_x,
                                                priv->pointer_y - priv->grab_y);

      casilda_compositor_toplevel_save_position (priv->grabbed_toplevel);
    }
  else if (priv->pointer_mode == CASILDA_POINTER_MODE_RESIZE)
    {
      casilda_compositor_handle_pointer_resize_toplevel (priv);
    }
  else
    {
      CasildaCompositorToplevel *toplevel;
      struct wlr_surface *surface;
      double sx, sy;

      toplevel = casilda_compositor_get_toplevel_at_pointer (priv, &surface, &sx, &sy);

      if (!toplevel)
        casilda_compositor_reset_cursor (priv);

      if (surface)
        {
          uint32_t time = gtk_event_controller_get_current_event_time (priv->motion_controller);
          wlr_seat_pointer_notify_enter (priv->seat, surface, sx, sy);
          wlr_seat_pointer_notify_motion (priv->seat, time, sx, sy);
        }
      else
        {
          wlr_seat_pointer_clear_focus (priv->seat);
        }
    }
}

static void
on_motion_controller_enter (G_GNUC_UNUSED GtkEventControllerMotion *self,
                            gdouble                                 x,
                            gdouble                                 y,
                            CasildaCompositorPrivate               *priv)
{
  casilda_compositor_handle_pointer_motion (priv, x, y);
  wlr_seat_pointer_notify_frame (priv->seat);
}

static void
on_motion_controller_leave (G_GNUC_UNUSED GtkEventControllerMotion *self,
                            CasildaCompositorPrivate               *priv)
{
  wlr_seat_pointer_clear_focus (priv->seat);
}

static void
on_motion_controller_motion (G_GNUC_UNUSED GtkEventControllerMotion *self,
                             gdouble                                 x,
                             gdouble                                 y,
                             CasildaCompositorPrivate               *priv)
{
  casilda_compositor_handle_pointer_motion (priv, x, y);
  wlr_seat_pointer_notify_frame (priv->seat);
}

static gboolean
on_scroll_controller_scroll_begin (G_GNUC_UNUSED GtkEventControllerScroll *self,
                                   CasildaCompositorPrivate               *priv)
{
  /* This is used to tell touchpads apart from trackpoints, as touchpads
   * have discrete "fingers appeared / fingers left" phases and trackpoints don't */
  priv->scroll_begun = true;

  return TRUE;
}

static gboolean
on_scroll_controller_scroll (GtkEventControllerScroll *self,
                             gdouble                   dx,
                             gdouble                   dy,
                             CasildaCompositorPrivate *priv)
{
  uint32_t time_msec = gtk_event_controller_get_current_event_time (GTK_EVENT_CONTROLLER (self));
  GdkScrollUnit unit = gtk_event_controller_scroll_get_unit (self);
  enum wl_pointer_axis_source source = priv->scroll_begun ? WL_POINTER_AXIS_SOURCE_FINGER : WL_POINTER_AXIS_SOURCE_CONTINUOUS;
  int32_t ddx = 0, ddy = 0;

  if (unit == GDK_SCROLL_UNIT_WHEEL)
    { /* Any wheel, hi-res or low-res (values are doubles, divided by 120 in the hi-res case) */
      ddx = dx * WLR_POINTER_AXIS_DISCRETE_STEP;
      ddy = dy * WLR_POINTER_AXIS_DISCRETE_STEP;
      source = WL_POINTER_AXIS_SOURCE_WHEEL;
    }
  /* Leave discrete values at 0 otherwise, wlroots interprets non-zero as specifically discrete events */

  if (dx != 0.0)
    wlr_seat_pointer_notify_axis (priv->seat,
                                  time_msec,
                                  WL_POINTER_AXIS_HORIZONTAL_SCROLL,
                                  dx,
                                  ddx,
                                  source,
                                  WL_POINTER_AXIS_RELATIVE_DIRECTION_IDENTICAL);

  if (dy != 0.0)
    wlr_seat_pointer_notify_axis (priv->seat,
                                  time_msec,
                                  WL_POINTER_AXIS_VERTICAL_SCROLL,
                                  dy,
                                  ddy,
                                  source,
                                  WL_POINTER_AXIS_RELATIVE_DIRECTION_IDENTICAL);

  wlr_seat_pointer_notify_frame (priv->seat);

  return TRUE;
}

static gboolean
on_scroll_controller_scroll_end (GtkEventControllerScroll *self,
                                 CasildaCompositorPrivate *priv)
{
  uint32_t time_msec = gtk_event_controller_get_current_event_time (GTK_EVENT_CONTROLLER (self));
  GdkScrollUnit unit = gtk_event_controller_scroll_get_unit (self);
  enum wl_pointer_axis_source source = priv->scroll_begun ? WL_POINTER_AXIS_SOURCE_FINGER : WL_POINTER_AXIS_SOURCE_CONTINUOUS;

  if (unit == GDK_SCROLL_UNIT_WHEEL)
    source = WL_POINTER_AXIS_SOURCE_WHEEL;

  /* XXX: should be harmless to always stop both axes */

  wlr_seat_pointer_notify_axis (priv->seat,
                                time_msec,
                                WL_POINTER_AXIS_HORIZONTAL_SCROLL,
                                0,
                                0,
                                source,
                                WL_POINTER_AXIS_RELATIVE_DIRECTION_IDENTICAL);

  wlr_seat_pointer_notify_axis (priv->seat,
                                time_msec,
                                WL_POINTER_AXIS_VERTICAL_SCROLL,
                                0,
                                0,
                                source,
                                WL_POINTER_AXIS_RELATIVE_DIRECTION_IDENTICAL);

  wlr_seat_pointer_notify_frame (priv->seat);
  priv->scroll_begun = false;

  return TRUE;
}

static void
casilda_compositor_focus_toplevel (CasildaCompositorToplevel *toplevel,
                                   struct wlr_surface        *surface)
{
  CasildaCompositorPrivate *priv = toplevel->priv;
  struct wlr_surface *focused_surface = priv->seat->keyboard_state.focused_surface;
  struct wlr_xdg_toplevel *xdg_toplevel = toplevel->xdg_toplevel;

  if (focused_surface == surface || toplevel->toplevels)
    return;

  if (focused_surface)
    {
      struct wlr_xdg_toplevel *focused_toplevel =
        wlr_xdg_toplevel_try_from_wlr_surface (focused_surface);

      if (focused_toplevel)
        wlr_xdg_toplevel_set_activated (focused_toplevel, false);
    }

  /* Move it to the front */
  wlr_xdg_toplevel_set_activated (xdg_toplevel, true);

  if (xdg_toplevel->parent)
    {
      CasildaCompositorToplevel *parent = xdg_toplevel->parent->base->data;
      if (parent)
        {
          parent->toplevels = g_list_remove (parent->toplevels, toplevel);
          parent->toplevels = g_list_prepend (parent->toplevels, toplevel);
        }
    }
  else
    {
      priv->toplevels = g_list_remove (priv->toplevels, toplevel);
      priv->toplevels = g_list_prepend (priv->toplevels, toplevel);
    }

  wlr_seat_keyboard_notify_enter (priv->seat,
                                  xdg_toplevel->base->surface,
                                  priv->keyboard.keycodes,
                                  priv->keyboard.num_keycodes,
                                  &priv->keyboard.modifiers);
}

static void
casilda_compositor_seat_pointer_notify (CasildaCompositorPrivate    *priv,
                                        gint                         button,
                                        enum wl_pointer_button_state state)
{
  uint32_t time_msec, wl_button;
  struct wlr_surface *surface = NULL;
  CasildaCompositorToplevel *toplevel;
  double sx, sy;

  if (button == 1)
    {
      wl_button = BTN_LEFT;
    }
  else if (button == 2)
    {
      wl_button = BTN_MIDDLE;
    }
  else if (button == 3)
    {
      wl_button = BTN_RIGHT;
    }
  else
    {
      g_warning ("%s unknown button %u", __func__, button);
      return;
    }

  time_msec = gtk_event_controller_get_current_event_time (GTK_EVENT_CONTROLLER (priv->click_gesture));

  wlr_seat_pointer_notify_button (priv->seat, time_msec, wl_button, state);
  wlr_seat_pointer_notify_frame (priv->seat);

  toplevel = casilda_compositor_get_toplevel_at_pointer (priv, &surface, &sx, &sy);

  if (state == WL_POINTER_BUTTON_STATE_RELEASED)
    casilda_compositor_reset_pointer_mode (priv);
  else if (toplevel)
    casilda_compositor_focus_toplevel (toplevel, surface);
}

static void
on_click_gesture_pressed (G_GNUC_UNUSED GtkGestureClick *self,
                          G_GNUC_UNUSED gint        n_press,
                          G_GNUC_UNUSED gdouble     x,
                          G_GNUC_UNUSED gdouble     y,
                          CasildaCompositorPrivate *priv)
{
  gint button = gtk_gesture_single_get_current_button (GTK_GESTURE_SINGLE (self));

  gtk_widget_grab_focus (priv->self);
  casilda_compositor_seat_pointer_notify (priv, button, WL_POINTER_BUTTON_STATE_PRESSED);
}

static void
on_click_gesture_released (G_GNUC_UNUSED GtkGestureClick *self,
                           G_GNUC_UNUSED gint        n_press,
                           G_GNUC_UNUSED gdouble     x,
                           G_GNUC_UNUSED gdouble     y,
                           CasildaCompositorPrivate *priv)
{
  gint button = gtk_gesture_single_get_current_button (GTK_GESTURE_SINGLE (self));

  casilda_compositor_seat_pointer_notify (priv, button, WL_POINTER_BUTTON_STATE_RELEASED);
}

static void
on_touchpad_swipe_event (GdkEvent                   *event,
                         uint32_t                    time_msec,
                         GdkTouchpadGesturePhase     phase,
                         CasildaCompositorPrivate   *priv)
{
  gdouble dx, dy;
  gboolean cancel = false;

  switch (phase)
    {
    case GDK_TOUCHPAD_GESTURE_PHASE_BEGIN:
      wlr_pointer_gestures_v1_send_swipe_begin (priv->pointer_gestures,
                                                priv->seat,
                                                time_msec,
                                                gdk_touchpad_event_get_n_fingers (event));
      break;
    case GDK_TOUCHPAD_GESTURE_PHASE_UPDATE:
      gdk_touchpad_event_get_deltas (event, &dx, &dy);
      wlr_pointer_gestures_v1_send_swipe_update(priv->pointer_gestures,
                                                priv->seat,
                                                time_msec,
                                                dx,
                                                dy);
      break;
    case GDK_TOUCHPAD_GESTURE_PHASE_CANCEL:
      cancel = true;
      /* will be followed by an END event */
      G_GNUC_FALLTHROUGH;
    case GDK_TOUCHPAD_GESTURE_PHASE_END:
      wlr_pointer_gestures_v1_send_swipe_end (priv->pointer_gestures,
                                              priv->seat,
                                              time_msec,
                                              cancel);
      break;
    default:
      break;
    }
}

static void
on_touchpad_pinch_event (GdkEvent                   *event,
                         uint32_t                    time_msec,
                         GdkTouchpadGesturePhase     phase,
                         CasildaCompositorPrivate   *priv)
{
  gdouble dx, dy;
  gboolean cancel = false;

  switch (phase)
    {
    case GDK_TOUCHPAD_GESTURE_PHASE_BEGIN:
      wlr_pointer_gestures_v1_send_pinch_begin (priv->pointer_gestures,
                                                priv->seat,
                                                time_msec,
                                                gdk_touchpad_event_get_n_fingers (event));
      break;
    case GDK_TOUCHPAD_GESTURE_PHASE_UPDATE:
      gdk_touchpad_event_get_deltas (event, &dx, &dy);
      wlr_pointer_gestures_v1_send_pinch_update(priv->pointer_gestures,
                                                priv->seat,
                                                time_msec,
                                                dx,
                                                dy,
                                                gdk_touchpad_event_get_pinch_scale (event),
                                                gdk_touchpad_event_get_pinch_angle_delta (event) * (180.0 / G_PI));
      break;
    case GDK_TOUCHPAD_GESTURE_PHASE_CANCEL:
      cancel = true;
      G_GNUC_FALLTHROUGH;
    case GDK_TOUCHPAD_GESTURE_PHASE_END:
      wlr_pointer_gestures_v1_send_pinch_end (priv->pointer_gestures,
                                              priv->seat,
                                              time_msec,
                                              cancel);
      break;
    default:
      break;
    }
}

static void
on_touchpad_hold_event (GdkEvent                   *event,
                        uint32_t                    time_msec,
                        GdkTouchpadGesturePhase     phase,
                        CasildaCompositorPrivate   *priv)
{
  gboolean cancel = false;

  switch (phase)
    {
    case GDK_TOUCHPAD_GESTURE_PHASE_BEGIN:
      wlr_pointer_gestures_v1_send_hold_begin (priv->pointer_gestures,
                                               priv->seat,
                                               time_msec,
                                               gdk_touchpad_event_get_n_fingers (event));
      break;
    case GDK_TOUCHPAD_GESTURE_PHASE_CANCEL:
      cancel = true;
      G_GNUC_FALLTHROUGH;
    case GDK_TOUCHPAD_GESTURE_PHASE_END:
      wlr_pointer_gestures_v1_send_hold_end (priv->pointer_gestures,
                                             priv->seat,
                                             time_msec,
                                             cancel);
      break;
    default:
      break;
    }
}

static gboolean
on_touchpad_gesture_controller_event (GtkEventControllerLegacy   *self,
                                      GdkEvent                   *event,
                                      CasildaCompositorPrivate   *priv)
{
  uint32_t time_msec = gtk_event_controller_get_current_event_time (GTK_EVENT_CONTROLLER (self));

  switch (gdk_event_get_event_type (event))
    {
    case GDK_TOUCHPAD_SWIPE:
      on_touchpad_swipe_event (event, time_msec, gdk_touchpad_event_get_gesture_phase (event), priv);
      return TRUE;
    case GDK_TOUCHPAD_PINCH:
      on_touchpad_pinch_event (event, time_msec, gdk_touchpad_event_get_gesture_phase (event), priv);
      return TRUE;
    case GDK_TOUCHPAD_HOLD:
      on_touchpad_hold_event (event, time_msec, gdk_touchpad_event_get_gesture_phase (event), priv);
      return TRUE;
    default:
      break;
    }

  return FALSE;
}

static xkb_mod_mask_t
gkeyboard_get_xkb_mod_mask (GdkDevice *gkeyboard)
{
  GdkModifierType state = gdk_device_get_modifier_state (gkeyboard);
  guint retval = 0;

  if (state & GDK_SHIFT_MASK)
    retval |= WLR_MODIFIER_SHIFT;
  if (state & GDK_LOCK_MASK)
    retval |= WLR_MODIFIER_CAPS;
  if (state & GDK_CONTROL_MASK)
    retval |= WLR_MODIFIER_CTRL;
  if (state & GDK_ALT_MASK)
    retval |= WLR_MODIFIER_ALT;
  if (state & GDK_SUPER_MASK)
    retval |= WLR_MODIFIER_LOGO;
  if (state & GDK_HYPER_MASK)
    retval |= WLR_MODIFIER_MOD2;
  if (state & GDK_META_MASK)
    retval |= WLR_MODIFIER_MOD3;

  return retval;
}


static void
casilda_compositor_seat_key_notify (GtkEventControllerKey    *self,
                                    CasildaCompositorPrivate *priv,
                                    uint32_t                  key,
                                    uint32_t                  state)
{
  uint32_t time_msec = gtk_event_controller_get_current_event_time (GTK_EVENT_CONTROLLER (self));
  xkb_mod_mask_t depressed = gkeyboard_get_xkb_mod_mask (priv->gkeyboard);

  /*
   * NOTE: we do not use GdkDevice:modifiers-state because that changes before we the the mod key press event
   * and we do not use EventControllerKey::modifiers signal because it changes after the mod key release
   */

  /* Send key event first */
  wlr_seat_keyboard_notify_key (priv->seat, time_msec, key - 8, state);


  /* Update modifiers if necessary after */
  if (priv->keyboard.modifiers.depressed != depressed)
    {
      priv->keyboard.modifiers.depressed = depressed;
      wlr_seat_keyboard_send_modifiers (priv->seat, &priv->keyboard.modifiers);
    }
}

static gboolean
on_key_controller_key_pressed (GtkEventControllerKey        *self,
                               G_GNUC_UNUSED guint           keyval,
                               guint                         keycode,
                               G_GNUC_UNUSED GdkModifierType state,
                               CasildaCompositorPrivate     *priv)
{
  casilda_compositor_seat_key_notify (self, priv, keycode, WL_KEYBOARD_KEY_STATE_PRESSED);
  return TRUE;
}

static void
on_key_controller_key_released (GtkEventControllerKey        *self,
                                G_GNUC_UNUSED guint           keyval,
                                guint                         keycode,
                                G_GNUC_UNUSED GdkModifierType state,
                                CasildaCompositorPrivate     *priv)
{
  casilda_compositor_seat_key_notify (self, priv, keycode, WL_KEYBOARD_KEY_STATE_RELEASED);
}

static void
cursor_handle_surface_commit (struct wl_listener *listener, void *data)
{
  CasildaCompositorPrivate *priv = wl_container_of (listener, priv, on_cursor_surface_commit);
  struct wlr_surface *surface = data;
  struct wlr_buffer *buffer = surface->current.buffer;

  if (!buffer)
    {
      g_debug ("Cursor surface committed without buffer");
      casilda_compositor_reset_cursor (priv);
      return;
    }

  g_autoptr(GdkTexture) tex = casilda_buffer_texture_from_wlr (buffer, NULL, NULL);

  if (!tex)
    {
      g_warning ("Failed to import cursor texture");
      return;
    }

  texture_debug_add_weak (tex);

  g_set_object (&priv->cursor_gdk_texture, tex);

  priv->hotspot_x -= surface->current.dx;
  priv->hotspot_y -= surface->current.dy;

  if (!tex)
    return;

  /* Finally create cursor from texture */
  g_autoptr (GdkCursor) gdk_cursor = gdk_cursor_new_from_texture (tex, priv->hotspot_x, priv->hotspot_y, NULL);
  g_set_object (&priv->cursor_gdk_cursor, gdk_cursor);

  /* Set cursor */
  if (gdk_cursor)
    gtk_widget_set_cursor (priv->self, priv->cursor_gdk_cursor);
}

static void
cursor_handle_surface_destroy (struct wl_listener *listener, G_GNUC_UNUSED void *data)
{
  CasildaCompositorPrivate *priv = wl_container_of (listener, priv, on_cursor_surface_destroy);

  casilda_compositor_cursor_handler_remove (priv);
}

static void
on_seat_request_cursor (struct wl_listener *listener, void *data)
{
  CasildaCompositorPrivate *priv = wl_container_of (listener, priv, on_request_cursor);
  struct wlr_seat_pointer_request_set_cursor_event *event = data;
  struct wlr_seat_client *focused_client = priv->seat->pointer_state.focused_client;
  struct wlr_surface *surface = event->surface;

  if (focused_client != event->seat_client)
    return;

  if (!surface)
    return;

  priv->hotspot_x = event->hotspot_x;
  priv->hotspot_y = event->hotspot_y;

  wlr_surface_send_enter (surface, &priv->output);

  /* We only keep track of the last cursor change */
  casilda_compositor_cursor_handler_remove (priv);

  /* Update cursor once the surface has been committed */
  priv->on_cursor_surface_commit.notify = cursor_handle_surface_commit;
  wl_signal_add (&surface->events.commit, &priv->on_cursor_surface_commit);

  priv->on_cursor_surface_destroy.notify = cursor_handle_surface_destroy;
  wl_signal_add (&surface->events.destroy, &priv->on_cursor_surface_destroy);
}

static bool
casilda_compositor_backend_start (struct wlr_backend *wlr_backend)
{
  CasildaCompositorPrivate *priv = wl_container_of (wlr_backend, priv, backend);
  g_info ("Starting Casilda backend at %s", priv->socket);
  return true;
}

static void
casilda_compositor_backend_destroy (struct wlr_backend *wlr_backend)
{
  CasildaCompositorPrivate *priv = wl_container_of (wlr_backend, priv, backend);

  wlr_backend_finish (&priv->backend);
  wlr_output_destroy (&priv->output);
}

static bool
casilda_compositor_output_commit (G_GNUC_UNUSED struct wlr_output             *wlr_output,
                                  G_GNUC_UNUSED const struct wlr_output_state *state)
{
  return TRUE;
}

static void
casilda_compositor_output_destroy (G_GNUC_UNUSED struct wlr_output *wlr_output)
{
  /* TODO: disconnect from GdkFrameClock */
}

static void
output_handle_bind(G_GNUC_UNUSED struct wl_listener *listener, void *data)
{
  const struct wlr_output_event_bind *e = data;
  struct wlr_output *o = e->output;

  wl_output_send_geometry (e->resource, 0, 0, o->phys_width, o->phys_height, o->subpixel, o->make, o->model, o->transform);
}

static void
casilda_compositor_backend_init (CasildaCompositorPrivate *priv)
{
  /* Backend implementation */
  priv->backend_impl.start = casilda_compositor_backend_start;
  priv->backend_impl.destroy = casilda_compositor_backend_destroy;

  /* Init wlroots backend */
  wlr_backend_init (&priv->backend, &priv->backend_impl);
}

static void
casilda_compositor_output_init (CasildaCompositorPrivate *priv)
{
  struct wlr_output_state state;

  wlr_output_state_init (&state);

  /* Initialize custom output iface */
  priv->output_impl.commit = casilda_compositor_output_commit;
  priv->output_impl.destroy = casilda_compositor_output_destroy;

  /* Actual size will be set on size_allocate() */
  wlr_output_state_set_custom_mode (&state, 0, 0, 0);

  wlr_output_state_set_scale (&state, priv->scale);

  /* Init wlr output */
  wlr_output_init (&priv->output,
                   &priv->backend,
                   &priv->output_impl,
                   wl_display_get_event_loop (priv->wl_display),
                   &state);

  /* Gtk Inspector uses make and model in the monitor information pane */
  priv->output.make = g_strdup("Casilda");
  priv->output.model = g_strdup(CASILDA_VERSION_S);

  wl_signal_add (&priv->output.events.bind, &priv->output_bind);
  priv->output_bind.notify = output_handle_bind;

  /* Set a name */
  wlr_output_set_name (&priv->output, "CasildaCompositor");
  wlr_output_set_description (&priv->output, "Wayland compositor widget for Gtk 4");

  /* Output manager, needed for Gtk get the right output geometry with fractional scaling */
  struct wlr_output_layout *output_layout = wlr_output_layout_create (priv->wl_display);

  wlr_output_layout_add_auto (output_layout, &priv->output);
  wlr_xdg_output_manager_v1_create (priv->wl_display, output_layout);

  /* Make output global */
  wlr_output_create_global (&priv->output, priv->wl_display);

  wlr_output_state_finish (&state);
}

static void
casilda_pointer_mode_init (CasildaCompositorPrivate *priv)
{
  wlr_pointer_init (&priv->pointer, NULL, "Casilda-pointer");

  priv->on_request_cursor.notify = on_seat_request_cursor;
  wl_signal_add (&priv->seat->events.request_set_cursor,
                 &priv->on_request_cursor);

  priv->motion_controller = gtk_event_controller_motion_new ();
  priv->scroll_controller = gtk_event_controller_scroll_new (GTK_EVENT_CONTROLLER_SCROLL_BOTH_AXES);
  priv->touchpad_gesture_controller = gtk_event_controller_legacy_new ();
  gtk_event_controller_set_propagation_phase (GTK_EVENT_CONTROLLER (priv->touchpad_gesture_controller), GTK_PHASE_BUBBLE);
  priv->click_gesture = gtk_gesture_click_new ();
  gtk_gesture_single_set_button (GTK_GESTURE_SINGLE (priv->click_gesture), 0);

  g_signal_connect (priv->motion_controller, "enter",
                    G_CALLBACK (on_motion_controller_enter),
                    priv);
  g_signal_connect (priv->motion_controller, "leave",
                    G_CALLBACK (on_motion_controller_leave),
                    priv);
  g_signal_connect (priv->motion_controller, "motion",
                    G_CALLBACK (on_motion_controller_motion),
                    priv);

  g_signal_connect (priv->scroll_controller, "scroll-begin",
                    G_CALLBACK (on_scroll_controller_scroll_begin),
                    priv);
  g_signal_connect (priv->scroll_controller, "scroll",
                    G_CALLBACK (on_scroll_controller_scroll),
                    priv);
  g_signal_connect (priv->scroll_controller, "scroll-end",
                    G_CALLBACK (on_scroll_controller_scroll_end),
                    priv);

  g_signal_connect (priv->touchpad_gesture_controller, "event",
                    G_CALLBACK (on_touchpad_gesture_controller_event),
                    priv);

  g_signal_connect (priv->click_gesture, "pressed",
                    G_CALLBACK (on_click_gesture_pressed),
                    priv);
  g_signal_connect (priv->click_gesture, "released",
                    G_CALLBACK (on_click_gesture_released),
                    priv);

  gtk_widget_add_controller (priv->self, priv->motion_controller);
  gtk_widget_add_controller (priv->self, priv->scroll_controller);
  gtk_widget_add_controller (priv->self, priv->touchpad_gesture_controller);
  gtk_widget_add_controller (priv->self, GTK_EVENT_CONTROLLER (priv->click_gesture));

  g_object_ref (priv->motion_controller);
  g_object_ref (priv->scroll_controller);
  g_object_ref (priv->touchpad_gesture_controller);
  g_object_ref (priv->click_gesture);
}

static struct xkb_keymap *
_gdk_device_get_xkb_keymap (GdkDevice *gkeyboard)
{
  struct xkb_keymap *keymap = NULL;
#ifdef GDK_WINDOWING_WAYLAND
  if (GDK_IS_WAYLAND_DEVICE (gkeyboard))
    {
      keymap = gdk_wayland_device_get_xkb_keymap (gkeyboard);
      xkb_keymap_ref (keymap);
    }
#endif

#if defined(GDK_WINDOWING_X11) && defined(HAVE_X11_XCB)
  if (GDK_IS_X11_DEVICE_XI2 (gkeyboard))
    {
G_GNUC_BEGIN_IGNORE_DEPRECATIONS
      struct xkb_context *context = xkb_context_new (XKB_CONTEXT_NO_FLAGS);
      Display *dpy = gdk_x11_display_get_xdisplay (GDK_X11_DISPLAY (gdk_device_get_display (gkeyboard)));

      keymap = xkb_x11_keymap_new_from_device (context,
                                               XGetXCBConnection (dpy),
                                               gdk_x11_device_get_id (gkeyboard),
                                               XKB_KEYMAP_COMPILE_NO_FLAGS);
      xkb_context_unref (context);
G_GNUC_END_IGNORE_DEPRECATIONS
    }
#endif

  /* Fallback to US */
  if (keymap == NULL)
    {
      struct xkb_context *context = xkb_context_new (XKB_CONTEXT_NO_FLAGS);
      keymap = xkb_keymap_new_from_names (context, NULL, XKB_KEYMAP_COMPILE_NO_FLAGS);
      xkb_context_unref (context);
    }

  return keymap;
}

static void
on_gdk_keyboard_notify (GObject *object, GParamSpec *pspec, CasildaCompositor *compositor)
{
  CasildaCompositorPrivate *priv = GET_PRIVATE(compositor);
  GdkDevice *gkeyboard = GDK_DEVICE (object);

  if (g_strcmp0 (pspec->name, "layout-names") == 0)
    {
      struct xkb_keymap *keymap = _gdk_device_get_xkb_keymap (gkeyboard);

      /* Set keymap */
      wlr_keyboard_set_keymap (&priv->keyboard, keymap);
      xkb_keymap_unref (keymap);
    }
  else if (g_strcmp0 (pspec->name, "active-layout-index") == 0)
    {
      gint i = gdk_device_get_active_layout_index (gkeyboard);
      if (i >= 0)
        {
          /* Update layout/group index*/
          priv->keyboard.modifiers.group = (guint) i;
          wlr_seat_keyboard_notify_modifiers (priv->seat, &priv->keyboard.modifiers);
        }
    }
  else if (g_strcmp0 (pspec->name, "caps-lock-state") == 0 ||
           g_strcmp0 (pspec->name, "scroll-lock-state") == 0 ||
           g_strcmp0 (pspec->name, "num-lock-state") == 0)
    {
      struct xkb_keymap *keymap = _gdk_device_get_xkb_keymap (gkeyboard);
      xkb_mod_mask_t locked = 0;

      if (gdk_device_get_caps_lock_state (priv->gkeyboard))
        locked |= (1 << xkb_keymap_mod_get_index (keymap, XKB_MOD_NAME_CAPS));
      if (gdk_device_get_scroll_lock_state (priv->gkeyboard))
        locked |= (1 << xkb_keymap_mod_get_index (keymap, XKB_VMOD_NAME_SCROLL));
      if (gdk_device_get_num_lock_state (priv->gkeyboard))
        locked |= (1 << xkb_keymap_mod_get_index (keymap, XKB_MOD_NAME_NUM));

      priv->keyboard.modifiers.locked = locked;
      wlr_seat_keyboard_notify_modifiers (priv->seat, &priv->keyboard.modifiers);
      xkb_keymap_unref (keymap);
    }
}

static void
casilda_compositor_keyboard_init (CasildaCompositorPrivate *priv)
{
  GdkDisplay *gdisplay;
  GdkSeat *gseat;

  wlr_keyboard_init (&priv->keyboard, NULL, "Casilda-keyboard");

  gdisplay = gtk_widget_get_display (priv->self);
  gseat = gdk_display_get_default_seat (gdisplay);
  priv->gkeyboard = g_object_ref (gdk_seat_get_keyboard (gseat));
  priv->gpointer = g_object_ref (gdk_seat_get_pointer (gseat));

  /* layout-names and active-layout-index notification */
  g_signal_connect_object (priv->gkeyboard, "notify", G_CALLBACK (on_gdk_keyboard_notify), priv->self, G_CONNECT_DEFAULT);

  wlr_seat_set_keyboard (priv->seat, &priv->keyboard);

  priv->key_controller = g_object_ref (gtk_event_controller_key_new ());
  g_signal_connect (priv->key_controller, "key-pressed",
                    G_CALLBACK (on_key_controller_key_pressed),
                    priv);
  g_signal_connect (priv->key_controller, "key-released",
                    G_CALLBACK (on_key_controller_key_released),
                    priv);

  /* This takes ownership */
  gtk_widget_add_controller (priv->self, priv->key_controller);
}

static void
casilda_compositor_init (CasildaCompositor *compositor)
{
  GtkWidget *widget = GTK_WIDGET (compositor);

  gtk_widget_set_overflow (widget, GTK_OVERFLOW_HIDDEN);
  gtk_widget_set_focusable (widget, TRUE);
}

static gboolean
on_drop_target_accept (G_GNUC_UNUSED GtkDropTargetAsync       *target,
                       G_GNUC_UNUSED GdkDrop                  *drop,
                       G_GNUC_UNUSED CasildaCompositorPrivate *priv)
{
  /* Always accept drags, we need to forward events to clients */
  return TRUE;
}

static gboolean
on_drop_target_drop (G_GNUC_UNUSED GtkDropTargetAsync *target,
                     GdkDrop                          *drop,
                     G_GNUC_UNUSED double              x,
                     G_GNUC_UNUSED double              y,
                     CasildaCompositorPrivate         *priv)
{
  GdkDragAction action = GDK_ACTION_NONE;

  if (priv->seat->drag_source)
    action = casilda_data_source_action_from_wl (priv->seat->drag_source->current_dnd_action);

  if (priv->drag)
    {
      gdk_drop_finish (drop, action);
    }
  else
    {
      /* Set action for CasildaDataSource to finish drag after finishing reading data from drop */
      g_object_set_data (G_OBJECT (drop), "dnd-action", GUINT_TO_POINTER (action));

      /* The real button release was consumed by Gtk so we need to fake a button release event */
      casilda_compositor_handle_pointer_motion (priv, x, y);
      casilda_compositor_seat_pointer_notify (priv, 1, WL_POINTER_BUTTON_STATE_RELEASED);
    }

  return action != GDK_ACTION_NONE;
}

static GdkDragAction
on_drop_target_drag_enter (G_GNUC_UNUSED GtkDropTargetAsync *target,
                           GdkDrop                          *drop,
                           gdouble                           x,
                           gdouble                           y,
                           CasildaCompositorPrivate         *priv)
{
  /* Start wlroots drag when drop comes from the host */
  if (!priv->drag && priv->toplevels)
    {
      /* We use the first toplevel as the source of the drag */
      CasildaCompositorToplevel *toplevel = priv->toplevels->data;
      struct wl_client *client = wl_resource_get_client (toplevel->xdg_toplevel->resource);
      struct wlr_seat_client *seat_client = wlr_seat_client_for_wl_client (priv->seat, client);
      struct wlr_data_source *data_source = casilda_data_source_new (G_OBJECT (drop));
      struct wlr_drag *drag = wlr_drag_create (seat_client, data_source, NULL);
      uint32_t serial;

      if (!drag)
        {
          wlr_data_source_destroy (data_source);
          return GDK_ACTION_NONE;
        }

      /* Fake button press for wlroots to use as the DnD start */
      wlr_seat_pointer_notify_enter (priv->seat, toplevel->xdg_toplevel->base->surface, -16, -16);
      serial = wlr_seat_pointer_notify_button (priv->seat,
                                               gtk_event_controller_get_current_event_time (GTK_EVENT_CONTROLLER (target)),
                                               BTN_LEFT,
                                               WL_POINTER_BUTTON_STATE_PRESSED);
      /* Use serial from button press */
      wlr_seat_start_pointer_drag (priv->seat, drag, serial);
    }

  casilda_compositor_handle_pointer_motion (priv, x, y);

  if (priv->seat->drag_source)
    return casilda_data_source_action_from_wl (priv->seat->drag_source->current_dnd_action);

  return GDK_ACTION_NONE;
}

static GdkDragAction
on_drop_target_drag_leave (G_GNUC_UNUSED GtkDropTargetAsync *target,
                           G_GNUC_UNUSED GdkDrop            *drop,
                           CasildaCompositorPrivate         *priv)
{
  if (!priv->drag && priv->seat->drag_source)
    wlr_data_source_destroy (priv->seat->drag_source);
  else
    wlr_seat_pointer_clear_focus (priv->seat);

  return GDK_ACTION_NONE;
}

static GdkDragAction
on_drop_target_drag_motion (G_GNUC_UNUSED GtkDropTargetAsync *target,
                            G_GNUC_UNUSED GdkDrop            *drop,
                            gdouble                           x,
                            gdouble                           y,
                            CasildaCompositorPrivate         *priv)
{
  casilda_compositor_handle_pointer_motion (priv, x, y);

  if (priv->seat->drag_source)
    return casilda_data_source_action_from_wl (priv->seat->drag_source->current_dnd_action);

  return GDK_ACTION_NONE;
}

static void
casilda_compositor_constructed (GObject *object)
{
  CasildaCompositorPrivate *priv = GET_PRIVATE (object);

  priv->self = GTK_WIDGET (object);

  priv->scale = 1.0;

  /* Toplevel state */
  priv->toplevel_state = g_hash_table_new_full (g_str_hash,
                                                g_str_equal,
                                                g_free,
                                                g_free);

  casilda_compositor_backend_init (priv);
  casilda_compositor_wlr_init (priv);
  casilda_compositor_output_init (priv);
  casilda_pointer_mode_init (priv);
  casilda_compositor_keyboard_init (priv);
  casilda_compositor_reset_pointer_mode (priv);

  /* Setup Drop target to track events during a DnD operation */
  GtkDropTargetAsync *drop_target = gtk_drop_target_async_new (NULL, GDK_ACTION_COPY|GDK_ACTION_MOVE|GDK_ACTION_LINK|GDK_ACTION_ASK);
  g_signal_connect (drop_target, "accept", G_CALLBACK (on_drop_target_accept), priv);
  g_signal_connect (drop_target, "drop", G_CALLBACK (on_drop_target_drop), priv);
  g_signal_connect (drop_target, "drag-enter", G_CALLBACK (on_drop_target_drag_enter), priv);
  g_signal_connect (drop_target, "drag-leave", G_CALLBACK (on_drop_target_drag_leave), priv);
  g_signal_connect (drop_target, "drag-motion", G_CALLBACK (on_drop_target_drag_motion), priv);
  gtk_widget_add_controller (GTK_WIDGET (object), GTK_EVENT_CONTROLLER (drop_target));
  g_set_object (&priv->drop_target, drop_target);

  priv->wl_source = casilda_wayland_source_new (priv->wl_display);
  g_source_attach (priv->wl_source, NULL);

  /* Start the backend. */
  if (!wlr_backend_start (&priv->backend))
    /* TODO: handle error */
    g_warning("Could not start backend");

  G_OBJECT_CLASS (casilda_compositor_parent_class)->constructed (object);
}

static void
casilda_compositor_dispose (GObject *object)
{
  CasildaCompositorPrivate *priv = GET_PRIVATE (object);

  g_clear_object (&priv->motion_controller);
  g_clear_object (&priv->scroll_controller);
  g_clear_object (&priv->touchpad_gesture_controller);
  g_clear_object (&priv->key_controller);
  g_clear_object (&priv->click_gesture);
  g_clear_object (&priv->adjustment[GTK_ORIENTATION_HORIZONTAL]);
  g_clear_object (&priv->adjustment[GTK_ORIENTATION_VERTICAL]);
  g_clear_object (&priv->gkeyboard);
  g_clear_object (&priv->gpointer);
  g_clear_object (&priv->drag_icon_texture);
  g_clear_object (&priv->drop_target);
  g_clear_object (&priv->drag);
  g_clear_object (&priv->clipboard_provider);
  g_clear_object (&priv->drag_provider);

  casilda_compositor_reset_cursor (priv);

  g_clear_object (&priv->gl_context);

  G_OBJECT_CLASS (casilda_compositor_parent_class)->dispose (object);
}

static void
casilda_compositor_finalize (GObject *object)
{
  CasildaCompositorPrivate *priv = GET_PRIVATE (object);

  /* Unlink signals */
  wl_list_remove (&priv->output_bind.link);
  wl_list_remove (&priv->new_xdg_toplevel.link);
  wl_list_remove (&priv->new_xdg_popup.link);
  wl_list_remove (&priv->request_activate.link);
  wl_list_remove (&priv->request_set_selection.link);
  wl_list_remove (&priv->request_set_shape.link);
  wl_list_remove (&priv->request_start_drag.link);

  wl_list_remove (&priv->on_request_cursor.link);

  casilda_compositor_cursor_handler_remove (priv);
  casilda_compositor_reset_drag_icon (priv);

  g_clear_pointer (&priv->toplevel_state, g_hash_table_destroy);
  g_clear_pointer (&priv->socket, g_free);

  wl_display_destroy_clients (priv->wl_display);

  wlr_keyboard_finish (&priv->keyboard);
  wlr_pointer_finish (&priv->pointer);
  wlr_backend_destroy (&priv->backend);

  g_source_destroy (priv->wl_source);
  g_clear_pointer (&priv->wl_source, g_source_unref);

  wl_display_destroy (priv->wl_display);

  G_OBJECT_CLASS (casilda_compositor_parent_class)->finalize (object);
}

static void
compositor_adjustment_value_changed (G_GNUC_UNUSED GtkAdjustment *adjustment, gpointer data)
{
  gtk_widget_queue_draw (GTK_WIDGET (data));
}

static void
compositor_set_adjustment (CasildaCompositor *compositor, GtkOrientation orientation, GtkAdjustment *adjustment)
{
  CasildaCompositorPrivate *priv = GET_PRIVATE (compositor);
  GtkAdjustment **adjustment_prop = &priv->adjustment[orientation];

  if (adjustment == *adjustment_prop)
    return;

  if (*adjustment_prop)
    g_signal_handlers_disconnect_by_func (*adjustment_prop, compositor_adjustment_value_changed, compositor);

  g_set_object (adjustment_prop, adjustment);

  if (adjustment)
    {
      g_signal_connect (adjustment, "value-changed", G_CALLBACK (compositor_adjustment_value_changed), compositor);

      compositor_adjustment_value_changed (adjustment, compositor);
    }
}

static void
casilda_compositor_set_property (GObject *object, guint prop_id, const GValue *value, GParamSpec *pspec)
{
  CasildaCompositorPrivate *priv;

  g_return_if_fail (CASILDA_IS_COMPOSITOR (object));
  priv = GET_PRIVATE (object);

  switch (prop_id)
    {
    case PROP_SOCKET:
      g_set_str (&priv->socket, g_value_get_string (value));
      break;
    case PROP_HADJUSTMENT:
      compositor_set_adjustment (CASILDA_COMPOSITOR (object), GTK_ORIENTATION_HORIZONTAL, g_value_get_object (value));
      break;
    case PROP_VADJUSTMENT:
      compositor_set_adjustment (CASILDA_COMPOSITOR (object), GTK_ORIENTATION_VERTICAL, g_value_get_object (value));
      break;
    case PROP_HSCROLL_POLICY:
    case PROP_VSCROLL_POLICY:
      g_warning ("Property %s is ignored", pspec->name);
      break;

    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
      break;
    }
}

static void
casilda_compositor_get_property (GObject *object, guint prop_id, GValue *value, GParamSpec *pspec)
{
  CasildaCompositorPrivate *priv;

  g_return_if_fail (CASILDA_IS_COMPOSITOR (object));
  priv = GET_PRIVATE (object);

  switch (prop_id)
    {
    case PROP_SOCKET:
      g_value_set_string (value, priv->socket);
      break;
    case PROP_HADJUSTMENT:
      g_value_set_object (value, priv->adjustment[GTK_ORIENTATION_HORIZONTAL]);
      break;
    case PROP_VADJUSTMENT:
      g_value_set_object (value, priv->adjustment[GTK_ORIENTATION_VERTICAL]);
      break;
    case PROP_HSCROLL_POLICY:
    case PROP_VSCROLL_POLICY:
      g_value_set_enum (value, GTK_SCROLL_NATURAL);
      break;
    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
      break;
    }
}

static void
on_casilda_compositor_frame_clock_update (G_GNUC_UNUSED GdkFrameClock *self, CasildaCompositorPrivate *priv)
{
  wlr_output_send_frame (&priv->output);
}

static void
on_casilda_compositor_clipboard_changed (G_GNUC_UNUSED GObject *obj, CasildaCompositorPrivate *priv)
{
  struct wlr_data_source *source = casilda_data_source_new (G_OBJECT (priv->clipboard));
  wlr_seat_set_selection (priv->seat, source, wl_display_next_serial (priv->seat->display));
}

static void
casilda_compositor_realize (GtkWidget *widget)
{
  CasildaCompositorPrivate *priv = GET_PRIVATE (widget);

  GTK_WIDGET_CLASS (casilda_compositor_parent_class)->realize (widget);

  priv->frame_clock = gtk_widget_get_frame_clock (widget);
  priv->frame_clock_source =
    g_signal_connect (priv->frame_clock, "update",
                      G_CALLBACK (on_casilda_compositor_frame_clock_update),
                      priv);

  priv->clipboard = gtk_widget_get_clipboard (widget);
  priv->clipboard_source =
    g_signal_connect (priv->clipboard, "changed",
                      G_CALLBACK (on_casilda_compositor_clipboard_changed),
                      priv);
}

static void
casilda_compositor_unrealize (GtkWidget *widget)
{
  CasildaCompositorPrivate *priv = GET_PRIVATE (widget);

  if (priv->frame_clock && priv->frame_clock_source)
    {
      g_signal_handler_disconnect (priv->frame_clock, priv->frame_clock_source);
      priv->frame_clock_source = 0;
    }

  priv->frame_clock = NULL;

  if (priv->clipboard && priv->clipboard_source)
    {
      g_signal_handler_disconnect (priv->clipboard, priv->clipboard_source);
      priv->clipboard_source = 0;
    }

  priv->clipboard = NULL;

  GTK_WIDGET_CLASS (casilda_compositor_parent_class)->unrealize (widget);
}

static void
casilda_compositor_state_flags_changed (GtkWidget *widget, GtkStateFlags previous_state_flags)
{
  GTK_WIDGET_CLASS (casilda_compositor_parent_class)->state_flags_changed (widget, previous_state_flags);

  /* Disable Drop state as user feedback will be provided by the embedded client */
  if (gtk_widget_get_state_flags (widget) & GTK_STATE_FLAG_DROP_ACTIVE)
    gtk_widget_unset_state_flags (widget, GTK_STATE_FLAG_DROP_ACTIVE);
}

static void
casilda_compositor_class_init (CasildaCompositorClass *klass)
{
  GObjectClass *object_class = G_OBJECT_CLASS (klass);
  GtkWidgetClass *widget_class = GTK_WIDGET_CLASS (klass);

  object_class->constructed = casilda_compositor_constructed;
  object_class->dispose = casilda_compositor_dispose;
  object_class->finalize = casilda_compositor_finalize;
  object_class->set_property = casilda_compositor_set_property;
  object_class->get_property = casilda_compositor_get_property;

  widget_class->snapshot = casilda_compositor_snapshot;
  widget_class->size_allocate = casilda_compositor_size_allocate;
  widget_class->realize = casilda_compositor_realize;
  widget_class->unrealize = casilda_compositor_unrealize;
  widget_class->state_flags_changed = casilda_compositor_state_flags_changed;

  /* GtkScrollable implementation */
  g_object_class_override_property (object_class, PROP_HADJUSTMENT,    "hadjustment");
  g_object_class_override_property (object_class, PROP_VADJUSTMENT,    "vadjustment");
  g_object_class_override_property (object_class, PROP_HSCROLL_POLICY, "hscroll-policy");
  g_object_class_override_property (object_class, PROP_VSCROLL_POLICY, "vscroll-policy");

  /* Properties */

  /**
   * CasildaCompositor:socket:
   *
   * Wayland socket the compositor will listen on.
   *
   * If NULL you can still use WAYLAND_SOCKET with an fd returned by
   * casilda_compositor_get_client_socket_fd() instead of setting up WAYLAND_DISPLAY.
   *
   */
  properties[PROP_SOCKET] =
    g_param_spec_string ("socket", "", "", NULL, G_PARAM_READWRITE | G_PARAM_CONSTRUCT_ONLY);

  g_object_class_install_properties (object_class, N_PROPERTIES, properties);
}

/* wlroots */

static void
seat_request_set_selection (struct wl_listener *listener, void *data)
{
  CasildaCompositorPrivate *priv = wl_container_of (listener, priv, request_set_selection);
  struct wlr_seat_request_set_selection_event *event = data;

  wlr_seat_set_selection (priv->seat, event->source, event->serial);

  /* Integrate with Gtk clipboard */
  g_set_object (&priv->clipboard_provider, casilda_content_provider_new (event->source));

  g_signal_handlers_block_by_func (priv->clipboard, on_casilda_compositor_clipboard_changed, priv);
  gdk_clipboard_set_content (priv->clipboard, priv->clipboard_provider);
  g_signal_handlers_unblock_by_func (priv->clipboard, on_casilda_compositor_clipboard_changed, priv);
}

static void
drag_icon_handle_surface_commit (struct wl_listener *listener, void *data)
{
  CasildaCompositorPrivate *priv = wl_container_of (listener, priv, on_drag_icon_surface_commit);
  struct wlr_surface *surface = data;
  struct wlr_buffer *buffer = surface->current.buffer;

  if (!buffer)
    {
      g_debug ("Drag icon surface committed without buffer");
      return;
    }

  g_autoptr(GdkTexture) tex = casilda_buffer_texture_from_wlr (buffer, NULL, NULL);

  if (!tex)
    {
      g_warning ("Failed to import drag icon texture");
      return;
    }

  texture_debug_add_weak (tex);

  g_set_object (&priv->drag_icon_texture, tex);

  /* Set drag icon */
  gtk_drag_icon_set_from_paintable (priv->drag,
                                    GDK_PAINTABLE (priv->drag_icon_texture),
                                    -surface->current.dx,
                                    -surface->current.dy);
}

static void
drag_icon_handle_surface_destroy (struct wl_listener *listener, G_GNUC_UNUSED void *data)
{
  CasildaCompositorPrivate *priv = wl_container_of (listener, priv, on_drag_icon_surface_destroy);
  casilda_compositor_reset_drag_icon (priv);
}

static void casilda_compositor_drag_end (CasildaCompositorPrivate *priv, gboolean success);

static void
on_drag_dnd_finished (G_GNUC_UNUSED GdkDrag *drag, CasildaCompositorPrivate *priv)
{
  casilda_compositor_drag_end (priv, TRUE);
}

static void
on_drag_cancel (G_GNUC_UNUSED GdkDrag *drag, G_GNUC_UNUSED GdkDragCancelReason reason, CasildaCompositorPrivate *priv)
{
  casilda_compositor_drag_end (priv, FALSE);
}

static void
casilda_compositor_drag_end (CasildaCompositorPrivate *priv, gboolean success)
{
  gtk_drop_target_async_set_formats (priv->drop_target, NULL);

  g_signal_handlers_disconnect_by_func (priv->drag, on_drag_dnd_finished, priv);
  g_signal_handlers_disconnect_by_func (priv->drag, on_drag_cancel, priv);

  gdk_drag_drop_done (priv->drag, success);
  g_clear_object (&priv->drag);

  casilda_compositor_seat_pointer_notify (priv, 1, WL_POINTER_BUTTON_STATE_RELEASED);

  wlr_seat_pointer_clear_focus (priv->seat);
}

static void
seat_request_start_drag (struct wl_listener *listener, void *data)
{
  CasildaCompositorPrivate *priv = wl_container_of (listener, priv, request_start_drag);
  struct wlr_seat_request_start_drag_event *event = data;
  struct wlr_drag *drag = event->drag;

  if (!wlr_seat_validate_pointer_grab_serial (priv->seat, event->origin, event->serial))
    {
      wlr_data_source_destroy (drag->source);
      return;
    }

  /* Hook up wlr drag */
  wlr_seat_start_pointer_drag (priv->seat, drag, event->serial);

  /* Create content provider for drag source */
  g_set_object (&priv->drag_provider, casilda_content_provider_new (drag->source));

  GdkDragAction actions = casilda_data_source_action_from_wl (priv->seat->drag_source->actions);
  g_autoptr (GdkContentFormats) formats = gdk_content_provider_ref_formats (priv->drag_provider);

  /* Update drop target */
  gtk_drop_target_async_set_formats (priv->drop_target, formats);
  gtk_drop_target_async_set_actions (priv->drop_target, actions);

  /* Create new Gdk drag with provider and actions */
  priv->drag = gdk_drag_begin (gtk_native_get_surface (gtk_widget_get_native (priv->self)),
                               priv->gpointer,
                               priv->drag_provider,
                               actions,
                               priv->pointer_x,
                               priv->pointer_y);

  g_signal_connect (priv->drag, "dnd-finished", G_CALLBACK (on_drag_dnd_finished), priv);
  g_signal_connect (priv->drag, "cancel", G_CALLBACK (on_drag_cancel), priv);

  if (drag->icon)
    {
      struct wlr_surface *surface = drag->icon->surface;

      /* Update drag icon once the surface has been committed */
      priv->on_drag_icon_surface_commit.notify = drag_icon_handle_surface_commit;
      wl_signal_add (&surface->events.commit, &priv->on_drag_icon_surface_commit);

      priv->on_drag_icon_surface_destroy.notify = drag_icon_handle_surface_destroy;
      wl_signal_add (&surface->events.destroy, &priv->on_drag_icon_surface_destroy);
    }
}

static void
xdg_toplevel_map (struct wl_listener *listener, G_GNUC_UNUSED void *data)
{
  CasildaCompositorToplevel *toplevel = wl_container_of (listener, toplevel, map);
  CasildaCompositorPrivate *priv = toplevel->priv;
  struct wlr_xdg_toplevel *xdg_toplevel = toplevel->xdg_toplevel;
  CasildaCompositorToplevelState *state = toplevel->state;
  struct wlr_box box;
  gint offset_x, offset_y;

  casilda_compositor_get_scroll_offset (priv, &offset_x, &offset_y);

  box = xdg_toplevel->base->geometry;

  if (xdg_toplevel->parent)
    {
      CasildaCompositorToplevel *parent = xdg_toplevel->parent->base->data;

      if (parent)
        {
          struct wlr_box parent_box = parent->xdg_toplevel->base->geometry;

          /* Start in the middle of the parent window and cap to 0,0 */
          toplevel->x = MAX (offset_x, parent->x + (parent_box.width - box.width) / 2);
          toplevel->y = MAX (offset_y, parent->y + (parent_box.height - box.height) / 2);

          parent->toplevels = g_list_prepend (parent->toplevels, toplevel);
        }
    }
  else
    {
      /* Start in the middle of the compositor viewport */
      toplevel->x = offset_x + MAX (0, (gtk_widget_get_width (toplevel->priv->self) - box.width) / 2);
      toplevel->y = offset_y + MAX (0, (gtk_widget_get_height (toplevel->priv->self) - box.height) / 2);

      toplevel->priv->toplevels = g_list_prepend (toplevel->priv->toplevels, toplevel);
    }

  if (state)
    {
      /* Restore this window state */
      xdg_toplevel->scheduled.fullscreen = state->fullscreen;
      xdg_toplevel->scheduled.maximized = state->maximized;

      g_debug ("%s %s %dx%d %dx%d maximized=%d fullscreen=%d",
               __func__,
               xdg_toplevel->app_id,
               state->x,
               state->y,
               state->width,
               state->height,
               state->maximized,
               state->fullscreen);

      if (state->fullscreen || state->maximized)
        {
          GtkWidget *widget = toplevel->priv->self;

          toplevel->old_state = *state;

          casilda_compositor_toplevel_configure (toplevel,
                                                 0, 0,
                                                 gtk_widget_get_width (widget),
                                                 gtk_widget_get_height (widget));
        }
      else
        {
          casilda_compositor_toplevel_configure (toplevel,
                                                 state->x,
                                                 state->y,
                                                 state->width,
                                                 state->height);
        }
    }
  else if (xdg_toplevel->requested.fullscreen || xdg_toplevel->requested.maximized)
    {
      GtkWidget *widget = toplevel->priv->self;

      casilda_compositor_toplevel_save_state (toplevel);

      xdg_toplevel->scheduled.fullscreen = xdg_toplevel->requested.fullscreen;
      xdg_toplevel->scheduled.maximized = xdg_toplevel->requested.maximized;

      casilda_compositor_toplevel_configure (toplevel,
                                             0, 0,
                                             gtk_widget_get_width (widget),
                                             gtk_widget_get_height (widget));
    }
  else
    casilda_compositor_focus_toplevel (toplevel, xdg_toplevel->base->surface);

  casilda_compositor_queue_draw (toplevel->priv);
}

static void
xdg_toplevel_unmap (struct wl_listener *listener, G_GNUC_UNUSED void *data)
{
  CasildaCompositorToplevel *toplevel = wl_container_of (listener, toplevel, unmap);
  struct wlr_xdg_toplevel *xdg_toplevel = toplevel->xdg_toplevel;

  if (toplevel == toplevel->priv->grabbed_toplevel)
    casilda_compositor_reset_pointer_mode (toplevel->priv);

  toplevel->state = NULL;

  if (xdg_toplevel->parent)
    {
      CasildaCompositorToplevel *parent = xdg_toplevel->parent->base->data;
      if (parent)
        {
          parent->toplevels = g_list_remove (parent->toplevels, toplevel);

          /* focus parent */
          casilda_compositor_focus_toplevel (parent, parent->xdg_toplevel->base->surface);
        }
    }
  else
    toplevel->priv->toplevels = g_list_remove (toplevel->priv->toplevels, toplevel);

  casilda_compositor_queue_draw (toplevel->priv);
}

static void
surface_commit (struct wlr_surface *surface)
{
  struct wlr_buffer *buffer = surface->current.buffer;
  GdkTexture **stored_texture = (GdkTexture **)&surface->data, *new_texture;

  if (!surface->mapped)
    g_clear_object (stored_texture);

  if (!buffer)
    return;

  new_texture = casilda_buffer_texture_from_wlr (buffer, &surface->current.buffer_damage, *stored_texture);
  g_clear_object (stored_texture);
  *stored_texture = new_texture;
}

static void
xdg_toplevel_commit (struct wl_listener *listener, G_GNUC_UNUSED void *data)
{
  CasildaCompositorToplevel *toplevel = wl_container_of (listener, toplevel, commit);

  surface_commit (toplevel->xdg_toplevel->base->surface);

  if (toplevel->xdg_toplevel->base->initial_commit)
    wlr_xdg_toplevel_set_size (toplevel->xdg_toplevel, 0, 0);
  else
    {
      struct wlr_box *geometry = &toplevel->xdg_toplevel->base->geometry;

      /* Update scrollable adjustment if window size changed */
      if (toplevel->last_commit_geometry.width != geometry->width || toplevel->last_commit_geometry.height != geometry->height)
        {
          toplevel->last_commit_geometry = *geometry;
          compositor_update_scrollable_adjustment (toplevel->priv);
        }
    }

  casilda_compositor_queue_draw (toplevel->priv);
  toplevel->needs_update = TRUE;
}


static void
xdg_subsurface_commit (struct wl_listener *listener, G_GNUC_UNUSED void *data)
{
  CasildaCompositorSubsurface *subsurface = wl_container_of (listener, subsurface, commit);

  surface_commit (subsurface->wlr_subsurface->surface);
  casilda_compositor_queue_draw (subsurface->priv);
}

static void
xdg_subsurface_destroy (struct wl_listener *listener, G_GNUC_UNUSED void *data)
{
  CasildaCompositorSubsurface *subsurface = wl_container_of (listener, subsurface, destroy);

  wl_list_remove (&subsurface->commit.link);
  wl_list_remove (&subsurface->destroy.link);

  /* Unref texture */
  g_clear_object (&subsurface->wlr_subsurface->surface->data);

  subsurface->parent->list = g_list_remove (subsurface->parent->list, subsurface);

  g_free (subsurface);
}

static void
xdg_subsurface_new_subsurface (struct wl_listener *listener, void *data)
{
  CasildaCompositorSurfaces *subsurfaces = wl_container_of (listener, subsurfaces, new_subsurface);
  struct wlr_subsurface *wlr_subsurface = data;
  struct wlr_xdg_toplevel *xdg_toplevel;
  struct wlr_xdg_popup *xdg_popup;

  CasildaCompositorSubsurface *subsurface = g_new0 (CasildaCompositorSubsurface, 1);

  if ((xdg_toplevel = wlr_xdg_toplevel_try_from_wlr_surface (wlr_subsurface->parent)))
    {
      CasildaCompositorToplevel *toplevel = xdg_toplevel->base->data;
      subsurface->priv = toplevel->priv;
    }
  else if ((xdg_popup = wlr_xdg_popup_try_from_wlr_surface(wlr_subsurface->parent)))
    {
      CasildaCompositorPopup *popup = xdg_popup->base->data;
      subsurface->priv = popup->priv;
    }

  subsurface->parent = subsurfaces;
  subsurface->wlr_subsurface = wlr_subsurface;

  subsurfaces->list = g_list_append (subsurfaces->list, subsurface);

  subsurface->commit.notify = xdg_subsurface_commit;
  wl_signal_add (&wlr_subsurface->surface->events.commit, &subsurface->commit);

  subsurface->destroy.notify = xdg_subsurface_destroy;
  wl_signal_add (&wlr_subsurface->events.destroy, &subsurface->destroy);

  surface_notify_scale (wlr_subsurface->surface, subsurface->priv->scale);
}


static void
compositor_subsurfaces_init (CasildaCompositorSurfaces *subsurfaces, struct wlr_surface *surface)
{
  subsurfaces->new_subsurface.notify = xdg_subsurface_new_subsurface;
  wl_signal_add (&surface->events.new_subsurface, &subsurfaces->new_subsurface);
}

static void
compositor_subsurfaces_fini (CasildaCompositorSurfaces *subsurfaces)
{
  wl_list_remove (&subsurfaces->new_subsurface.link);
}

static void
xdg_toplevel_destroy (struct wl_listener *listener, G_GNUC_UNUSED void *data)
{
  CasildaCompositorToplevel *toplevel = wl_container_of (listener, toplevel, destroy);

  casilda_compositor_cursor_handler_remove(toplevel->priv);

  wl_list_remove (&toplevel->map.link);
  wl_list_remove (&toplevel->unmap.link);
  wl_list_remove (&toplevel->commit.link);
  wl_list_remove (&toplevel->destroy.link);
  wl_list_remove (&toplevel->request_move.link);
  wl_list_remove (&toplevel->request_resize.link);
  wl_list_remove (&toplevel->request_maximize.link);
  wl_list_remove (&toplevel->request_fullscreen.link);
  wl_list_remove (&toplevel->set_app_id.link);

  compositor_subsurfaces_fini (&toplevel->subsurfaces);

  /* FIXME: need to do something if these are not empty */
  g_list_free (toplevel->toplevels);
  g_list_free (toplevel->popups);

  /* Unref texture */
  g_clear_object (&toplevel->xdg_toplevel->base->surface->data);

  g_free (toplevel);
}

static gboolean
casilda_compositor_toplevel_has_focus (CasildaCompositorToplevel *toplevel)
{
  CasildaCompositorPrivate *priv = toplevel->priv;
  struct wlr_surface *focused_surface = priv->seat->pointer_state.focused_surface;

  if (focused_surface)
    return toplevel->xdg_toplevel->base->surface == wlr_surface_get_root_surface (focused_surface);

  return FALSE;
}

static void
xdg_toplevel_request_move (struct wl_listener *listener, G_GNUC_UNUSED void *data)
{
  CasildaCompositorToplevel *toplevel = wl_container_of (listener, toplevel, request_move);
  CasildaCompositorPrivate *priv = toplevel->priv;

  if (!casilda_compositor_toplevel_has_focus (toplevel))
    return;

  priv->grabbed_toplevel = toplevel;
  priv->pointer_mode = CASILDA_POINTER_MODE_MOVE;
  priv->grab_x = priv->pointer_x - toplevel->x;
  priv->grab_y = priv->pointer_y - toplevel->y;
}

static void
xdg_toplevel_request_resize (struct wl_listener *listener, void *data)
{
  CasildaCompositorToplevel *toplevel = wl_container_of (listener, toplevel, request_resize);
  CasildaCompositorPrivate *priv = toplevel->priv;
  struct wlr_xdg_toplevel_resize_event *event = data;
  struct wlr_box box;
  double border_x, border_y;

  if (!casilda_compositor_toplevel_has_focus (toplevel))
    return;

  priv->grabbed_toplevel = toplevel;
  priv->pointer_mode = CASILDA_POINTER_MODE_RESIZE;
  priv->resize_edges = event->edges;

  box = toplevel->xdg_toplevel->base->geometry;

  border_x = toplevel->x + box.x +
             ((event->edges & WLR_EDGE_RIGHT) ? box.width : 0);
  border_y = toplevel->y + box.y +
             ((event->edges & WLR_EDGE_BOTTOM) ? box.height : 0);
  priv->grab_x = priv->pointer_x - border_x;
  priv->grab_y = priv->pointer_y - border_y;

  priv->grab_box = box;
  priv->grab_box.x += toplevel->x;
  priv->grab_box.y += toplevel->y;
}

static void
xdg_toplevel_request_maximize (struct wl_listener *listener, G_GNUC_UNUSED void *data)
{
  CasildaCompositorToplevel *toplevel =
    wl_container_of (listener, toplevel, request_maximize);

  casilda_compositor_toplevel_toggle_maximize_fullscreen (toplevel, FALSE);
}

static void
xdg_toplevel_request_fullscreen (struct wl_listener *listener, G_GNUC_UNUSED void *data)
{
  CasildaCompositorToplevel *toplevel =
    wl_container_of (listener, toplevel, request_fullscreen);

  casilda_compositor_toplevel_toggle_maximize_fullscreen (toplevel, TRUE);
}

static void
xdg_toplevel_set_app_id (struct wl_listener *listener, G_GNUC_UNUSED void *data)
{
  CasildaCompositorToplevel *toplevel = wl_container_of (listener, toplevel, set_app_id);
  const gchar *app_id = toplevel->xdg_toplevel->app_id;

  /*
   * NOTE: set_app_id is not supported
   * Instead it is used as a window unique id to keep track of windows state
   * Ideally this should be implemented with a session extension.
   */
  if (!g_str_has_prefix (app_id, "Casilda:"))
    return;

  toplevel->state = g_hash_table_lookup (toplevel->priv->toplevel_state, app_id);

  if (!toplevel->state)
    {
      /* Allocate new state struct */
      toplevel->state = g_new0 (CasildaCompositorToplevelState, 1);

      /* Start new windows in the top left corner */
      toplevel->state->x = 32;
      toplevel->state->y = 32;

      /* Insert it in out server hash table */
      g_hash_table_insert (toplevel->priv->toplevel_state,
                           g_strdup (app_id),
                           toplevel->state);
    }

  g_debug ("%s %s %dx%d %dx%d",
           __func__,
           toplevel->xdg_toplevel->app_id,
           toplevel->state->x,
           toplevel->state->y,
           toplevel->state->width,
           toplevel->state->height);
}

static void
server_new_xdg_toplevel (struct wl_listener *listener, void *data)
{
  CasildaCompositorPrivate *priv = wl_container_of (listener, priv, new_xdg_toplevel);
  struct wlr_xdg_toplevel *xdg_toplevel = data;
  CasildaCompositorToplevel *toplevel;

  toplevel = g_new0 (CasildaCompositorToplevel, 1);
  toplevel->priv = priv;
  toplevel->xdg_toplevel = xdg_toplevel;

  /* Back Reference */
  toplevel->xdg_toplevel->base->data = toplevel;

  toplevel->map.notify = xdg_toplevel_map;
  wl_signal_add (&xdg_toplevel->base->surface->events.map, &toplevel->map);
  toplevel->unmap.notify = xdg_toplevel_unmap;
  wl_signal_add (&xdg_toplevel->base->surface->events.unmap, &toplevel->unmap);
  toplevel->commit.notify = xdg_toplevel_commit;
  wl_signal_add (&xdg_toplevel->base->surface->events.commit, &toplevel->commit);

  compositor_subsurfaces_init (&toplevel->subsurfaces, xdg_toplevel->base->surface);

  toplevel->destroy.notify = xdg_toplevel_destroy;
  wl_signal_add (&xdg_toplevel->events.destroy, &toplevel->destroy);

  toplevel->request_move.notify = xdg_toplevel_request_move;
  wl_signal_add (&xdg_toplevel->events.request_move, &toplevel->request_move);
  toplevel->request_resize.notify = xdg_toplevel_request_resize;
  wl_signal_add (&xdg_toplevel->events.request_resize, &toplevel->request_resize);
  toplevel->request_maximize.notify = xdg_toplevel_request_maximize;
  wl_signal_add (&xdg_toplevel->events.request_maximize, &toplevel->request_maximize);
  toplevel->request_fullscreen.notify = xdg_toplevel_request_fullscreen;
  wl_signal_add (&xdg_toplevel->events.request_fullscreen, &toplevel->request_fullscreen);

  toplevel->set_app_id.notify = xdg_toplevel_set_app_id;
  wl_signal_add (&xdg_toplevel->events.set_app_id, &toplevel->set_app_id);

  surface_notify_scale (xdg_toplevel->base->surface, priv->scale);
}

static CasildaCompositorToplevel *
get_popup_root_toplevel (CasildaCompositorPopup *popup)
{
  if (popup->toplevel)
    return popup->toplevel;

  return get_popup_root_toplevel (popup->parent);
}

/* Leave a margin so that popups are not right next to the compositor border */
#define POSITIONER_MARGIN 4

static void
xdg_popup_commit (struct wl_listener *listener, G_GNUC_UNUSED void *data)
{
  CasildaCompositorPopup *popup = wl_container_of (listener, popup, commit);
  CasildaCompositorPrivate *priv = popup->priv;

  surface_commit (popup->xdg_popup->base->surface);

  if (popup->xdg_popup->base->initial_commit)
    {
      CasildaCompositorToplevel *toplevel = get_popup_root_toplevel (popup);
      struct wlr_box *geo = &toplevel->xdg_toplevel->base->geometry;
      gint offset_x, offset_y;

      casilda_compositor_get_scroll_offset (priv, &offset_x, &offset_y);

      struct wlr_box box = {
        .x = offset_x + ((toplevel->x - geo->x) * -1) + POSITIONER_MARGIN,
        .y = offset_y + ((toplevel->y - geo->y) * -1) + POSITIONER_MARGIN,
        .width = gtk_widget_get_width (priv->self) - POSITIONER_MARGIN * 2,
        .height = gtk_widget_get_height (priv->self) - POSITIONER_MARGIN * 2,
      };

      /* Define popup position box in parent toplevel coordinates */
      wlr_xdg_popup_unconstrain_from_box (popup->xdg_popup, &box);
    }

  casilda_compositor_queue_draw (priv);
}

static void
xdg_popup_destroy (struct wl_listener *listener, G_GNUC_UNUSED void *data)
{
  CasildaCompositorPopup *popup = wl_container_of (listener, popup, destroy);

  if (popup->toplevel)
    popup->toplevel->popups = g_list_remove (popup->toplevel->popups, popup);

  if (popup->parent)
    popup->parent->popups = g_list_remove (popup->parent->popups, popup);

  wl_list_remove (&popup->commit.link);
  wl_list_remove (&popup->destroy.link);

  compositor_subsurfaces_fini (&popup->subsurfaces);

  g_list_free (popup->popups);

  /* Clear texture */
  g_clear_object (&popup->xdg_popup->base->surface->data);

  g_free (popup);
}

static void
server_new_xdg_popup (G_GNUC_UNUSED struct wl_listener *listener, void *data)
{
  CasildaCompositorPrivate *priv = wl_container_of (listener, priv, new_xdg_popup);
  struct wlr_xdg_toplevel *parent_xdg_toplevel;
  struct wlr_xdg_popup *xdg_popup = data;
  struct wlr_xdg_surface *parent;
  CasildaCompositorPopup *popup;

  if(!(parent = wlr_xdg_surface_try_from_wlr_surface (xdg_popup->parent)))
    return;

  popup = g_new0 (CasildaCompositorPopup, 1);
  popup->priv = priv;
  popup->xdg_popup = xdg_popup;

  /* Back Reference */
  popup->xdg_popup->base->data = popup;

  /* We do not know if parent wlr_xdg_surface is from a toplevel or popup */
  if ((parent_xdg_toplevel = wlr_xdg_toplevel_try_from_wlr_surface (parent->surface)))
    {
      CasildaCompositorToplevel *toplevel = parent_xdg_toplevel->base->data;
      popup->toplevel = toplevel;
      toplevel->popups = g_list_prepend (toplevel->popups, popup);
    }
  else {
    struct wlr_xdg_popup *parent_xdg_popup = wlr_xdg_popup_try_from_wlr_surface(parent->surface);

    if (parent_xdg_popup)
      {
        CasildaCompositorPopup *parent_popup = parent_xdg_popup->base->data;
        popup->parent = parent_popup;
        parent_popup->popups = g_list_prepend (parent_popup->popups, popup);
      }
  }

  popup->commit.notify = xdg_popup_commit;
  wl_signal_add (&xdg_popup->base->surface->events.commit, &popup->commit);

  popup->destroy.notify = xdg_popup_destroy;
  wl_signal_add (&xdg_popup->events.destroy, &popup->destroy);

  compositor_subsurfaces_init (&popup->subsurfaces, xdg_popup->base->surface);

  surface_notify_scale (xdg_popup->base->surface, priv->scale);

  casilda_compositor_queue_draw (popup->priv);
}

static CasildaCompositorToplevel *
casilda_compositor_get_toplevel_from_xdg (CasildaCompositorPrivate *priv, struct wlr_xdg_toplevel *xdg_toplevel)
{
  if (!xdg_toplevel)
    return NULL;

  for (GList *l = priv->toplevels; l; l = g_list_next (l))
    {
      CasildaCompositorToplevel *toplevel = l->data;

      if (toplevel->xdg_toplevel == xdg_toplevel)
        return toplevel;
    }

  return NULL;
}


static void
server_request_activate (struct wl_listener *listener, void *data)
{
  CasildaCompositorPrivate *priv = wl_container_of (listener, priv, request_activate);
  struct wlr_xdg_activation_v1_request_activate_event *event = data;
  struct wlr_xdg_toplevel *xdg_toplevel = wlr_xdg_toplevel_try_from_wlr_surface (event->surface);
  CasildaCompositorToplevel *toplevel;

  toplevel = casilda_compositor_get_toplevel_from_xdg (priv, xdg_toplevel);

  if (toplevel)
    casilda_compositor_focus_toplevel (toplevel, xdg_toplevel->base->surface);
}


static void
server_request_set_shape (struct wl_listener *listener, void *data)
{
  CasildaCompositorPrivate *priv = wl_container_of (listener, priv, request_set_shape);
  struct wlr_cursor_shape_manager_v1_request_set_shape_event *event = data;

  /* Set cursor from name */
  gtk_widget_set_cursor_from_name (priv->self, wlr_cursor_shape_v1_name(event->shape));
}

static void
casilda_compositor_wlr_init (CasildaCompositorPrivate *priv)
{
  priv->wl_display = wl_display_create ();

#ifdef ENABLE_DMABUF
  if (g_getenv ("CASILDA_FORCE_SOFTWARE") == NULL)
    casilda_buffer_configure_dmabuf (priv->wl_display);
#endif

  casilda_buffer_configure_shm (priv->wl_display);

  wlr_compositor_create (priv->wl_display, 6, NULL);
  wlr_subcompositor_create (priv->wl_display);
  wlr_data_device_manager_create (priv->wl_display);

  wlr_viewporter_create (priv->wl_display);
  wlr_fractional_scale_manager_v1_create (priv->wl_display, 1);

  /* Set up xdg-shell version 6, needed for WM Capabilities */
  struct wlr_xdg_shell *xdg_shell = wlr_xdg_shell_create (priv->wl_display, 6);
  priv->new_xdg_toplevel.notify = server_new_xdg_toplevel;
  wl_signal_add (&xdg_shell->events.new_toplevel, &priv->new_xdg_toplevel);
  priv->new_xdg_popup.notify = server_new_xdg_popup;
  wl_signal_add (&xdg_shell->events.new_popup, &priv->new_xdg_popup);

  /* Set up xdg-activation */
  struct wlr_xdg_activation_v1 *xdg_activation = wlr_xdg_activation_v1_create (priv->wl_display);
  priv->request_activate.notify = server_request_activate;
  wl_signal_add (&xdg_activation->events.request_activate, &priv->request_activate);

  /* Set up cursor-shape-v1 */
  struct wlr_cursor_shape_manager_v1 *cursor_shape_manager = wlr_cursor_shape_manager_v1_create (priv->wl_display, 2);
  priv->request_set_shape.notify = server_request_set_shape;
  wl_signal_add (&cursor_shape_manager->events.request_set_shape, &priv->request_set_shape);

  /* Set up pointer-gestures-v1 */
  priv->pointer_gestures = wlr_pointer_gestures_v1_create (priv->wl_display);

  /* Configure seat */
  priv->seat = wlr_seat_create (priv->wl_display, "seat0");
  priv->request_set_selection.notify = seat_request_set_selection;
  wl_signal_add (&priv->seat->events.request_set_selection, &priv->request_set_selection);

  priv->request_start_drag.notify = seat_request_start_drag;
  wl_signal_add (&priv->seat->events.request_start_drag, &priv->request_start_drag);

  wlr_seat_set_capabilities (priv->seat, WL_SEAT_CAPABILITY_POINTER | WL_SEAT_CAPABILITY_KEYBOARD);

  /* xdg_foreign */
  priv->foreign_registry = wlr_xdg_foreign_registry_create(priv->wl_display);
  wlr_xdg_foreign_v1_create(priv->wl_display, priv->foreign_registry);
  wlr_xdg_foreign_v2_create(priv->wl_display, priv->foreign_registry);

  if (!priv->socket)
    return;

  if (wl_display_add_socket (priv->wl_display, priv->socket))
    g_warning ("Error adding socket file %s", priv->socket);
  else
    g_info ("Listening on %s", priv->socket);
}


/* Public API */

/**
 * casilda_compositor_new:
 * @socket: the named socket to use or NULL
 *
 * Create a new `CasildaCompositor` widget using @socket as the name of the Wayland socket.
 * Clients can connect to the compositor by setting WAYLAND_DISPLAY=@socket
 *
 * Returns: a new `CasildaCompositor` widget
 */
CasildaCompositor *
casilda_compositor_new (const gchar *socket)
{
  return g_object_new (CASILDA_COMPOSITOR_TYPE, "socket", socket, NULL);
}


/**
 * casilda_compositor_get_client_socket_fd:
 * @compositor: a `CasildaCompositor`
 *
 * Create a client socket file descriptor connected to this compositor ready to use by passing it to a client with
 * WAYLAND_SOCKET environment variable.
 * Once the returned FD is passed to the client it must be closed on the parent otherwise the client windows
 * will not get destroyed if the client looses the connection to the server.
 *
 * Returns: a socket FD connected to the compositor
 */
int
casilda_compositor_get_client_socket_fd (CasildaCompositor *compositor)
{
  g_return_val_if_fail (CASILDA_IS_COMPOSITOR (compositor), -1);

  CasildaCompositorPrivate *priv = GET_PRIVATE (compositor);
  gint fds[2] = {0, };

  if (socketpair (AF_UNIX, SOCK_STREAM, 0, fds))
    {
      g_warning ("Could not create a UNIX socketpair");
      return -1;
    }

  if (!wl_client_create (priv->wl_display, fds[0]))
    {
      g_warning ("Could not add socketpair to display");
      return  -1;
    }

  return fds[1];
}


/**
 * casilda_compositor_spawn_async:
 * @compositor: a `CasildaCompositor`
 * @working_directory: (type filename) (nullable): child's current working directory, or %NULL to inherit parent's
 * @argv: (array zero-terminated=1) (element-type filename): child's argument vector
 * @envp: (array zero-terminated=1) (element-type filename) (nullable): child's environment, or %NULL to inherit parent's
 * @flags: flags from #GSpawnFlags
 * @child_setup: (scope async) (closure user_data) (nullable): function to run in the child just before `exec()`
 * @user_data: user data for @child_setup
 * @child_pid: (out) (optional): return location for child process reference, or %NULL
 * @error: return location for error
 *
 * Executes a child program asynchronously with the right environment to automatically connect to this compositor.
 *
 * See [func@GLib.spawn_async_with_pipes_and_fds] for a full description; this function simply calls
 * [func@GLib.spawn_async_with_pipes_and_fds] without any pipes and with WAYLAND_DISPLAY set to `CasildaCompositor::socket` or
 * a fd already connected to the compositor and set to WAYLAND_SOCKET if its NULL.
 *
 * Please note GDK_BACKEND, WAYLAND_DISPLAY and WAYLAND_SOCKET are set by this function they are ignored from %envp and
 * DISPLAY is removed to avoid clients try to connect using X11
 *
 * Returns: TRUE on success, FALSE if error is set.
 */
gboolean
casilda_compositor_spawn_async (CasildaCompositor *compositor,
                                const gchar *working_directory,
                                gchar **argv,
                                gchar **envp,
                                GSpawnFlags flags,
                                GSpawnChildSetupFunc child_setup,
                                gpointer user_data,
                                GPid *child_pid,
                                GError **error)
{
  g_return_val_if_fail (CASILDA_IS_COMPOSITOR (compositor), FALSE);

  CasildaCompositorPrivate *priv = GET_PRIVATE (compositor);
  g_autoptr (GStrvBuilder) builder = g_strv_builder_new ();
  g_autofree gchar *wayland_socket = NULL;
  g_auto (GStrv) environ = NULL;
  GStrv source_env = NULL;
  gboolean retval;
  gint fd = -1;

  if (envp)
    source_env = envp;
  else
    source_env = environ = g_get_environ();

  /* Build environment */
  for (gint i = 0; source_env[i]; i++)
    {
      if (g_str_has_prefix (source_env[i], "DISPLAY="))
        continue;
      if (g_str_has_prefix (source_env[i], "GDK_BACKEND="))
        continue;
      if (g_str_has_prefix (source_env[i], "WAYLAND_DISPLAY="))
        continue;
      if (g_str_has_prefix (source_env[i], "WAYLAND_SOCKET="))
        continue;

      g_strv_builder_add (builder, source_env[i]);
    }

  /* Force GTK apps to wayland backend */
  g_strv_builder_add (builder, "GDK_BACKEND=wayland");

  if (priv->socket)
    wayland_socket = g_strdup_printf ("WAYLAND_DISPLAY=%s", priv->socket);
  else
    {
      fd = casilda_compositor_get_client_socket_fd (compositor);
      wayland_socket = g_strdup_printf ("WAYLAND_SOCKET=%d", fd);
    }

  /* Add wayland socket env var */
  g_strv_builder_add (builder, wayland_socket);

  g_auto (GStrv) env = g_strv_builder_end (builder);

  retval = g_spawn_async_with_pipes_and_fds (working_directory,
                                             (const gchar* const* ) argv,
                                             (const gchar* const* ) env,
                                             flags,
                                             child_setup,
                                             user_data,
                                             -1, -1, -1,
                                             &fd, &fd, fd > 0 ? 1 : 0,
                                             child_pid,
                                             NULL, NULL, NULL,
                                             error);

  /* Close file descriptor after its being passed to the client */
  if (fd > 0)
    close (fd);

  return retval;
}

