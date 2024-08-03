<?php
// Função para exibir campos personalizados no conteúdo do post
function anatelnews_display_custom_fields($content) {
    if (is_singular('post')) {
        $custom_fields = get_post_meta(get_the_ID());
        // Exemplo de exibição de campos personalizados
        // Ajuste conforme necessário para exibir os campos específicos do seu plugin
        foreach ($custom_fields as $key => $value) {
            $content .= '<p>' . esc_html($key) . ': ' . esc_html($value[0]) . '</p>';
        }
    }
    return $content;
}
add_filter('the_content', 'anatelnews_display_custom_fields');
?>
