/*
 * Casilda Data Source Integration
 *
 * Copyright (C) 2026  Juan Pablo Ugarte
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

#define WLR_USE_UNSTABLE 1
#define _POSIX_C_SOURCE 200809L

#include <fcntl.h>
#include <glib-unix.h>
#include <gio/gunixinputstream.h>
#include <gio/gunixoutputstream.h>
#include <wlr/types/wlr_data_device.h>
#include "casilda-private.h"

typedef struct
{
  struct wlr_data_source base;
  GObject *gdk_source;
} CasildaDataSource;

typedef struct
{
  GObject *gdk_source;
  gchar *mime_type;
  gint fd;
} SourceData;

static SourceData *
source_data_new (GObject *gdk_source, const gchar *mime_type, gint fd)
{
  SourceData *data = g_new0 (SourceData, 1);

  data->gdk_source = g_object_ref (gdk_source);
  data->mime_type = g_strdup (mime_type);
  data->fd = fd;

  return data;
}

static void
source_data_free (SourceData *data)
{
  g_clear_object (&data->gdk_source);
  g_free (data->mime_type);
  if (data->fd)
    close (data->fd);

  g_free (data);
}

static void
on_gdk_source_send_splice_done (GObject *stream, GAsyncResult *result, gpointer userdata)
{
  SourceData *data = userdata;
  GError *error = NULL;

  g_output_stream_splice_finish (G_OUTPUT_STREAM (stream), result, &error);

  if (GDK_IS_DROP (data->gdk_source))
    {
      GdkDragAction action = GPOINTER_TO_UINT (g_object_get_data (data->gdk_source, "dnd-action"));

      /* Finish drop operation */
      gdk_drop_finish (GDK_DROP (data->gdk_source), action);
    }

  source_data_free (data);
}

static void
on_gdk_source_send_read_done (G_GNUC_UNUSED GObject *obj, GAsyncResult *result, gpointer userdata)
{
  SourceData *data = userdata;
  GInputStream *stream = NULL;

  if (GDK_IS_DROP (data->gdk_source))
    stream = gdk_drop_read_finish (GDK_DROP (data->gdk_source), result, NULL, NULL);
  if (GDK_IS_CLIPBOARD (data->gdk_source))
    stream = gdk_clipboard_read_finish (GDK_CLIPBOARD (data->gdk_source), result, NULL, NULL);

  if (!stream)
    {
      source_data_free (data);
      return;
    }

  GOutputStream *output = g_unix_output_stream_new (data->fd, FALSE);

  g_output_stream_splice_async (output,
                                stream,
                                G_OUTPUT_STREAM_SPLICE_CLOSE_TARGET,
                                G_PRIORITY_DEFAULT,
                                NULL,
                                on_gdk_source_send_splice_done,
                                data);
}

static GdkContentFormats *
casilda_data_source_gdk_ref_formats (GObject *gdk_source)
{
  if (GDK_IS_CLIPBOARD (gdk_source))
    return gdk_content_formats_ref (gdk_clipboard_get_formats (GDK_CLIPBOARD (gdk_source)));
  if (GDK_IS_DROP (gdk_source))
    return gdk_content_formats_ref (gdk_drop_get_formats (GDK_DROP (gdk_source)));

  return NULL;
}

static void
casilda_data_source_send (struct wlr_data_source *data_source, const char *mime_type, int32_t fd)
{
  CasildaDataSource *source = (CasildaDataSource *)data_source;
  g_autoptr (GdkContentFormats) formats = casilda_data_source_gdk_ref_formats (source->gdk_source);
  const gchar *mimes[2] = { mime_type, NULL };

  if (!g_strv_contains (gdk_content_formats_get_mime_types (formats, NULL), mime_type))
    return;

  SourceData *data = source_data_new (source->gdk_source, mime_type, fd);

  if (GDK_IS_DROP (source->gdk_source))
    gdk_drop_read_async (GDK_DROP (source->gdk_source),
                         mimes,
                         G_PRIORITY_DEFAULT,
                         NULL,
                         on_gdk_source_send_read_done,
                         data);
  else if (GDK_IS_CLIPBOARD (source->gdk_source))
    gdk_clipboard_read_async (GDK_CLIPBOARD (source->gdk_source),
                              mimes,
                              G_PRIORITY_DEFAULT,
                              NULL,
                              on_gdk_source_send_read_done,
                              data);
  else
    source_data_free (data);
}


static void
casilda_data_source_destroy (struct wlr_data_source *data_source)
{
  CasildaDataSource *source = (CasildaDataSource *)data_source;
  g_clear_object (&source->gdk_source);
  g_free (source);
}

static const struct wlr_data_source_impl casilda_data_source_impl = {
  .send = casilda_data_source_send,
  .destroy = casilda_data_source_destroy,
};


struct wlr_data_source *
casilda_data_source_new (GObject *gdk_source)
{
  g_return_val_if_fail (GDK_IS_DROP (gdk_source) || GDK_IS_CLIPBOARD (gdk_source), NULL);

  CasildaDataSource *source = g_new0 (CasildaDataSource, 1);

  wlr_data_source_init (&source->base, &casilda_data_source_impl);

  /* This object will be used as the source of the data */
  source->gdk_source = g_object_ref (gdk_source);

  /* Set wlr dnd actions */
  if (GDK_IS_DROP (gdk_source))
    source->base.actions = casilda_data_source_dnd_action_from_gdk (gdk_drop_get_actions (GDK_DROP (gdk_source)));

  /* Copy supported mime types to new source */
  g_autoptr(GdkContentFormats) formats = casilda_data_source_gdk_ref_formats (gdk_source);
  for (const gchar * const *mime = gdk_content_formats_get_mime_types (formats, NULL); mime && *mime; mime++)
    {
      char **dst = wl_array_add (&source->base.mime_types, sizeof(char *));
      *dst = g_strdup (*mime);
    }

  return &source->base;
}


GdkDragAction
casilda_data_source_action_from_wl (enum wl_data_device_manager_dnd_action actions)
{
  GdkDragAction retval = 0;

  if (actions & WL_DATA_DEVICE_MANAGER_DND_ACTION_COPY)
    retval |= GDK_ACTION_COPY;
  if (actions & WL_DATA_DEVICE_MANAGER_DND_ACTION_MOVE)
    retval |= GDK_ACTION_MOVE;
  if (actions & WL_DATA_DEVICE_MANAGER_DND_ACTION_ASK)
    retval |= GDK_ACTION_ASK;

  return retval;
}


enum wl_data_device_manager_dnd_action
casilda_data_source_dnd_action_from_gdk (GdkDragAction actions)
{
  enum wl_data_device_manager_dnd_action retval = 0;

  if (actions & GDK_ACTION_COPY)
    retval |= WL_DATA_DEVICE_MANAGER_DND_ACTION_COPY;
  if (actions & GDK_ACTION_MOVE)
    retval |= WL_DATA_DEVICE_MANAGER_DND_ACTION_MOVE;
  if (actions & GDK_ACTION_ASK)
    retval |= WL_DATA_DEVICE_MANAGER_DND_ACTION_ASK;

  return retval;
}



