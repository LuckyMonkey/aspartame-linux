/*
 * Casilda Content Provider
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

#include <wlr/types/wlr_data_device.h>
#include <fcntl.h>
#include <glib-unix.h>
#include <gio/gunixinputstream.h>
#include <gio/gunixoutputstream.h>
#include "casilda-private.h"

#define CASILDA_CONTENT_PROVIDER_TYPE (casilda_content_provider_get_type ())
G_DECLARE_FINAL_TYPE (CasildaContentProvider, casilda_content_provider, CASILDA, CONTENT_PROVIDER, GdkContentProvider)

typedef struct
{
  struct wlr_data_source *source;

  struct wl_listener on_destroy;
} CasildaContentProviderPrivate;


struct _CasildaContentProvider
{
  GdkContentProvider parent;
};

enum {
  PROP_0,
  PROP_SOURCE,

  N_PROPERTIES
};

static GParamSpec *properties[N_PROPERTIES];

G_DEFINE_TYPE_WITH_PRIVATE (CasildaContentProvider, casilda_content_provider, GDK_TYPE_CONTENT_PROVIDER);

#define GET_PRIVATE(d) ((CasildaContentProviderPrivate *) casilda_content_provider_get_instance_private ((CasildaContentProvider *) d))

static void
casilda_content_provider_init (G_GNUC_UNUSED CasildaContentProvider *provider)
{

}

static void
casilda_content_provide_handle_source_destroy (struct wl_listener *listener, G_GNUC_UNUSED void *data)
{
  CasildaContentProviderPrivate *priv = wl_container_of (listener, priv, on_destroy);

  wl_list_remove (&priv->on_destroy.link);
  priv->source = NULL;
}

static void
casilda_content_provider_set_property (GObject *object, guint prop_id, const GValue *value, GParamSpec *pspec)
{
  CasildaContentProviderPrivate *priv;

  g_return_if_fail (CASILDA_IS_CONTENT_PROVIDER (object));
  priv = GET_PRIVATE (object);

  switch (prop_id)
    {
    case PROP_SOURCE:
      priv->source = g_value_get_pointer (value);

      priv->on_destroy.notify = casilda_content_provide_handle_source_destroy;
      wl_signal_add (&priv->source->events.destroy, &priv->on_destroy);
      break;
    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
      break;
    }
}

static void
casilda_content_provider_get_property (GObject *object, guint prop_id, GValue *value, GParamSpec *pspec)
{
  CasildaContentProviderPrivate *priv;

  g_return_if_fail (CASILDA_IS_CONTENT_PROVIDER (object));
  priv = GET_PRIVATE (object);

  switch (prop_id)
    {
    case PROP_SOURCE:
      g_value_set_pointer (value, priv->source);
      break;
    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
      break;
    }
}

static GdkContentFormats *
casilda_content_provider_ref_formats (GdkContentProvider *provider)
{
  CasildaContentProviderPrivate *priv = GET_PRIVATE (provider);
  GdkContentFormatsBuilder *builder;
  char **mime;

  if (!priv->source)
    return NULL;

  builder = gdk_content_formats_builder_new ();

  wl_array_for_each (mime, &priv->source->mime_types)
    gdk_content_formats_builder_add_mime_type (builder, *mime);

  return gdk_content_formats_builder_free_to_formats (builder);
}

static void
gdk_content_provider_bytes_write_mime_type_done (GObject *stream, GAsyncResult *result, gpointer task)
{
  GError *error = NULL;

  g_output_stream_splice_finish (G_OUTPUT_STREAM (stream), result, &error);

  if (error)
    g_task_return_error (task, error);
  else
    g_task_return_boolean (task, TRUE);

  g_object_unref (task);
}

static void
casilda_content_provider_write_mime_type_async (GdkContentProvider *provider,
                                                const char         *mime_type,
                                                GOutputStream      *stream,
                                                int                 io_priority,
                                                GCancellable       *cancellable,
                                                GAsyncReadyCallback callback,
                                                gpointer            user_data)
{
  CasildaContentProviderPrivate *priv = GET_PRIVATE (provider);
  GUnixPipe p;
  GTask *task;

  if (!priv->source)
    return;

  if (!g_unix_pipe_open (&p, O_CLOEXEC | O_NONBLOCK, NULL))
    return;

  task = g_task_new (provider, cancellable, callback, user_data);
  g_task_set_priority (task, io_priority);
  g_task_set_source_tag (task, casilda_content_provider_write_mime_type_async);

  gboolean mime_found;
  char **mime;

  wl_array_for_each (mime, &priv->source->mime_types)
    if ((mime_found = g_strcmp0 (mime_type, *mime) == 0))
        break;

  if (!mime_found)
    {
      g_task_return_new_error (task, G_IO_ERROR, G_IO_ERROR_NOT_SUPPORTED, "Cannot provide contents as “%s”", mime_type);
      g_object_unref (task);
      return;
    }

  /* Write data to pipe */
  wlr_data_source_send (priv->source, mime_type, g_unix_pipe_get (&p, G_UNIX_PIPE_END_WRITE));

  /* Read data from pipe */
  GInputStream *source = g_unix_input_stream_new (g_unix_pipe_get (&p, G_UNIX_PIPE_END_READ), TRUE);

  /* Write source to stream */
  g_output_stream_splice_async (stream,
                                source,
                                G_OUTPUT_STREAM_SPLICE_CLOSE_SOURCE,
                                io_priority,
                                cancellable,
                                gdk_content_provider_bytes_write_mime_type_done,
                                task);
}

static gboolean
casilda_content_provider_write_mime_type_finish (GdkContentProvider *provider, GAsyncResult *result, GError **error)
{
  g_return_val_if_fail (g_task_is_valid (result, provider), FALSE);
  g_return_val_if_fail (g_task_get_source_tag (G_TASK (result)) == casilda_content_provider_write_mime_type_async, FALSE);

  return g_task_propagate_boolean (G_TASK (result), error);
}

static void
casilda_content_provider_class_init (CasildaContentProviderClass *klass)
{
  GObjectClass *object_class = G_OBJECT_CLASS (klass);
  GdkContentProviderClass *provider_class = GDK_CONTENT_PROVIDER_CLASS (klass);

  object_class->set_property = casilda_content_provider_set_property;
  object_class->get_property = casilda_content_provider_get_property;

  provider_class->ref_formats = casilda_content_provider_ref_formats;
  provider_class->write_mime_type_async = casilda_content_provider_write_mime_type_async;
  provider_class->write_mime_type_finish = casilda_content_provider_write_mime_type_finish;

  properties[PROP_SOURCE] =
    g_param_spec_pointer ("source", "", "", G_PARAM_READWRITE | G_PARAM_CONSTRUCT_ONLY);

  g_object_class_install_properties (object_class, N_PROPERTIES, properties);
}


GdkContentProvider *
casilda_content_provider_new (struct wlr_data_source *source)
{
  return g_object_new (CASILDA_CONTENT_PROVIDER_TYPE, "source", source, NULL);
}
