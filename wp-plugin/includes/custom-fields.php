<?php
// Função para adicionar campos personalizados
function anatelnews_add_custom_box() {
    add_meta_box(
        'anatelnews_sectionid', // ID
        'Anatel News', // Título
        'anatelnews_custom_box_html', // Callback
        'post' // Tipo de post
    );
}

function anatelnews_custom_box_html($post) {
    $fields = [
        'anatel_URL' => 'URL',
        'anatel_Titulo' => 'Título',
        'anatel_SubTitulo' => 'Subtítulo',
        'anatel_ImagemChamada' => 'Imagem Chamada',
        'anatel_Descricao' => 'Descrição',
        'anatel_DataPublicacao' => 'Data de Publicação',
        'anatel_DataAtualizacao' => 'Data de Atualização',
        'anatel_ImagemPrincipal' => 'Imagem Principal',
        'anatel_TextMateria' => 'Texto Matéria',
        'anatel_Categoria' => 'Categoria'
    ];

    foreach ($fields as $field => $label) {
        $value = get_post_meta($post->ID, $field, true);
        echo "<label for='$field'>$label</label>";
        echo "<input type='text' name='$field' id='$field' value='$value' />";
        echo "<br>";
    }
}

// Função para salvar campos personalizados
function anatelnews_save_postdata($post_id) {
    $fields = [
        'anatel_URL',
        'anatel_Titulo',
        'anatel_SubTitulo',
        'anatel_ImagemChamada',
        'anatel_Descricao',
        'anatel_DataPublicacao',
        'anatel_DataAtualizacao',
        'anatel_ImagemPrincipal',
        'anatel_TextMateria',
        'anatel_Categoria'
    ];

    foreach ($fields as $field) {
        if (array_key_exists($field, $_POST)) {
            update_post_meta($post_id, $field, $_POST[$field]);
        }
    }
}

add_action('add_meta_boxes', 'anatelnews_add_custom_box');
add_action('save_post', 'anatelnews_save_postdata');
