<?php
// Exibir campos personalizados no frontend do WordPress
function anatelnews_display_custom_fields($content) {
    if (is_single() && 'post' == get_post_type()) {
        $custom_fields = get_post_meta(get_the_ID());

        if (!empty($custom_fields)) {
            $custom_content = '<div class="custom-fields">';
            foreach ($custom_fields as $key => $value) {
                if (strpos($key, 'anatel_') !== false) {
                    $custom_content .= '<p><strong>' . esc_html($key) . ':</strong> ' . esc_html($value[0]) . '</p>';
                }
            }
            $custom_content .= '</div>';
            $content .= $custom_content;
        }
    }

    return $content;
}
add_filter('the_content', 'anatelnews_display_custom_fields');
