import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:path/path.dart' as p;

class ApiService {
  static String normalizeBaseUrl(String baseUrl) {
    return baseUrl.trim().replaceAll(RegExp(r'/+$'), '');
  }

  static final Dio _dio = Dio(
    BaseOptions(
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 60),
      sendTimeout: const Duration(seconds: 60),
    ),
  );

  static Future<Map<String, dynamic>> login({
    required String baseUrl,
    required String username,
    required String password,
  }) async {
    final url = '${normalizeBaseUrl(baseUrl)}/api/login/';

    final response = await _dio.post(
      url,
      data: {
        'username': username,
        'password': password,
        'usuario': username,
        'senha': password,
      },
      options: Options(
        headers: {'Content-Type': 'application/json'},
      ),
    );

    if (response.data is Map<String, dynamic>) {
      return response.data as Map<String, dynamic>;
    }

    return {'success': false, 'message': 'Resposta inválida do servidor'};
  }

  static Future<List<dynamic>> fetchCampos({
    required String baseUrl,
  }) async {
    final url = '${normalizeBaseUrl(baseUrl)}/api/campos/';

    final response = await _dio.get(url);

    final data = response.data;

    if (data is List) return data;
    if (data is Map && data['results'] is List) {
      return data['results'] as List<dynamic>;
    }

    return [];
  }

  static Future<Map<String, dynamic>> sincronizarCadastro(
    Map<String, dynamic> cadastro, {
    required String baseUrl,
    String? fotoPath,
  }) async {
    final url = '${normalizeBaseUrl(baseUrl)}/api/cadastros/criar/';

    final formMap = <String, dynamic>{
      'id_ponto': (cadastro['id_ponto'] ?? '').toString(),
      'nome_cadastrador': (cadastro['nome_cadastrador'] ?? '').toString(),
      'usuario': (cadastro['nome_cadastrador'] ?? '').toString(),
      'data_cadastro': (cadastro['data_cadastro'] ?? '').toString(),
      'hora_cadastro': (cadastro['hora_cadastro'] ?? '').toString(),
      'latitude': (cadastro['latitude'] ?? '').toString(),
      'longitude': (cadastro['longitude'] ?? '').toString(),
      'status_sincronizacao':
          (cadastro['status_sincronizacao'] ?? 'Sincronizado').toString(),
      'dados_extras': jsonEncode(cadastro['dados_extras'] ?? {}),
    };

    if (fotoPath != null && fotoPath.trim().isNotEmpty) {
      formMap['foto'] = await MultipartFile.fromFile(
        fotoPath,
        filename: p.basename(fotoPath),
      );
    }

    final formData = FormData.fromMap(formMap);

    final response = await _dio.post(
      url,
      data: formData,
      options: Options(
        // Deixa o Dio montar o boundary corretamente
        contentType: 'multipart/form-data',
      ),
    );

    if (response.data is Map<String, dynamic>) {
      return response.data as Map<String, dynamic>;
    }

    return {'success': false, 'message': 'Resposta inválida do servidor'};
  }
}