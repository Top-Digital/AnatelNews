<?php
// Função para registrar campos personalizados na API REST
function anatelnews_register_custom_fields() {
    $fields = [
        'anatel_URL', 'anatel_Titulo', 'anatel_SubTitulo',
        'anatel_ImagemChamada', 'anatel_Descricao', 'anatel_DataPublicacao',
        'anatel_DataAtualizacao', 'anatel_ImagemPrincipal', 'anatel_TextMateria',
        'anatel_Categoria', 'wordpress_DataPublicacao', 'wordpress_DataAtualizacao',
        'mailchimp_DataEnvio'
    ];

    foreach ($fields as $field) {
        register_meta('post', $field, [
            'show_in_rest' => true,
            'single' => true,
            'type' => 'string',
        ]);
    }
}
add_action('rest_api_init', 'anatelnews_register_custom_fields');
?>
