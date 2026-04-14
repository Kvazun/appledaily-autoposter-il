<?php
/**
 * AppleDaily — Custom REST API Endpoint
 * Добавить в functions.php темы WordPress
 *
 * Эндпоинт: /wp-json/appledaily/v1/post
 * Auth header: X-AppDaily-Token
 *
 * Поддерживаемые поля POST (JSON):
 *   title       (string, required)
 *   content     (string, required)
 *   image_url   (string, optional) — URL изображения для featured image
 *   category    (string, optional) — slug категории
 */

// Инициализируем токен при первой загрузке
if ( ! get_option( 'appledaily_api_token' ) ) {
    update_option( 'appledaily_api_token', 'AppleDailyILToken2025Secret' );
}

// Регистрируем кастомный REST-маршрут
add_action( 'rest_api_init', function () {
    register_rest_route( 'appledaily/v1', '/post', array(
        'methods'             => 'POST',
        'callback'            => 'appledaily_create_post',
        'permission_callback' => 'appledaily_check_token',
    ) );
} );

// Проверка токена из заголовка X-AppDaily-Token
function appledaily_check_token( $request ) {
    $token  = $request->get_header( 'X-AppDaily-Token' );
    $stored = get_option( 'appledaily_api_token', '' );
    return ( $stored !== '' && hash_equals( $stored, (string) $token ) );
}

// Создание записи в WordPress
function appledaily_create_post( $request ) {
    $params  = $request->get_json_params();
    $title     = sanitize_text_field( $params['title'] ?? '' );
    $content   = wp_kses_post( $params['content'] ?? '' );
    $image_url = esc_url_raw( $params['image_url'] ?? '' );
    $category  = sanitize_text_field( $params['category'] ?? '' );

    if ( empty( $title ) ) {
        return new WP_Error( 'missing_title', 'Title required', array( 'status' => 400 ) );
    }

    // Определяем категорию
    $cat_ids = array();
    if ( ! empty( $category ) ) {
        $term = get_term_by( 'slug', $category, 'category' );
        if ( $term ) {
            $cat_ids[] = $term->term_id;
        }
    }

    $post_data = array(
        'post_title'    => $title,
        'post_content'  => $content,
        'post_status'   => 'publish',
        'post_author'   => 1,
    );

    if ( ! empty( $cat_ids ) ) {
        $post_data['post_category'] = $cat_ids;
    }

    $post_id = wp_insert_post( $post_data, true );

    if ( is_wp_error( $post_id ) ) {
        return new WP_Error( 'create_failed', $post_id->get_error_message(), array( 'status' => 500 ) );
    }

    // Устанавливаем featured image если передан URL
    if ( ! empty( $image_url ) ) {
        $attachment_id = appledaily_sideload_image( $image_url, $post_id );
        if ( $attachment_id && ! is_wp_error( $attachment_id ) ) {
            set_post_thumbnail( $post_id, $attachment_id );
        }
    }

    return array(
        'id'   => $post_id,
        'link' => get_permalink( $post_id ),
    );
}

// Загрузка внешнего изображения в медиатеку WordPress
function appledaily_sideload_image( $url, $post_id ) {
    require_once ABSPATH . 'wp-admin/includes/media.php';
    require_once ABSPATH . 'wp-admin/includes/file.php';
    require_once ABSPATH . 'wp-admin/includes/image.php';

    $attachment_id = media_sideload_image( $url, $post_id, '', 'id' );
    return $attachment_id;
}
