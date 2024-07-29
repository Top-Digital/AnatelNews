<?php
// Exibir campos personalizados no frontend do WordPress
function anatelnews_display_custom_fields() {
    global $post;

    // Verifica se é um post do tipo 'post' e se está em uma categoria específica
    if (is_single() && 'post' == get_post_type($post->ID)) {
        $custom_fields = get_post_meta($post->ID);

        if (!empty($custom_fields)) {
            echo '<div class="custom-fields">';
            foreach ($custom_fields as $key => $value) {
                if (strpos($key, 'anatel_') !== false) {
                    echo '<p><strong>' . esc_html($key) . ':</strong> ' . esc_html($value[0]) . '</p>';
                }
            }
            echo '</div>';
        }
    }
}
add_action('the_content', 'anatelnews_display_custom_fields');
