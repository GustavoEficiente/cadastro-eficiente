import 'dart:io';
import 'dart:convert';
import 'package:dio/dio.dart';

class ApiService {
  static const String baseUrl = 'http://192.168.1.22:8000';

  static final Dio _dio = Dio(
    BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 20),
      receiveTimeout: const Duration(seconds: 20),
      sendTimeout: const Duration(seconds: 20),
      headers: {
        'Accept': 'application/json',
      },
      validateStatus: (status) {
        return status != null && status < 500;
      },
    ),
  );

  // ================= LOGIN =================
  static Future<Map<String, dynamic>> login({
    required String username,
    required String password,
  }) async {
    try {
      final response = await _dio.post(
        '/api/login/',
        data: {
          'username': username,
          'password': password,
        },
        options: Options(
          contentType: Headers.formUrlEncodedContentType,
        ),
      );

      if (response.data is Map<String, dynamic>) {
        return Map<String, dynamic>.from(response.data);
      }

      return {
        'ok': false,
        'mensagem': 'Resposta inválida do servidor.',
      };
    } on DioException catch (e) {
      return {
        'ok': false,
        'mensagem': 'Não foi possível conectar ao servidor.',
        'erro': e.response?.data?.toString() ?? e.message ?? e.toString(),
        'status_code': e.response?.statusCode,
      };
    } catch (e) {
      return {
        'ok': false,
        'mensagem': 'Erro inesperado.',
        'erro': e.toString(),
      };
    }
  }

  // ================= CAMPOS =================
  static Future<List<dynamic>> buscarCampos() async {
    final response = await _dio.get('/api/campos/');
    if (response.data is List) {
      return response.data as List<dynamic>;
    }
    return [];
  }

  // ================= CADASTRO =================
  static Future<Map<String, dynamic>> sincronizarCadastro(
    Map<String, dynamic> payload,
  ) async {
    try {
      final Map<String, dynamic> formDataMap = {
        'id_ponto': payload['id_ponto'] ?? '',
        'nome_cadastrador': payload['nome_cadastrador'] ?? '',
        'data_cadastro': payload['data_cadastro'] ?? '',
        'hora_cadastro': payload['hora_cadastro'] ?? '',
        'latitude': payload['latitude']?.toString() ?? '',
        'longitude': payload['longitude']?.toString() ?? '',
        'status_sincronizacao':
            payload['status_sincronizacao'] ?? 'sincronizado',
        'dados_extras': payload['dados_extras'] is String
            ? payload['dados_extras']
            : jsonEncode(payload['dados_extras'] ?? {}),
      };

      final fotos = payload['fotos'];
      if (fotos is List) {
        for (int i = 0; i < fotos.length && i < 5; i++) {
          final caminho = fotos[i]?.toString() ?? '';
          if (caminho.isNotEmpty && await File(caminho).exists()) {
            formDataMap['foto_${i + 1}'] = await MultipartFile.fromFile(
              caminho,
              filename: caminho.split(Platform.pathSeparator).last,
            );
          }
        }
      }

      final formData = FormData.fromMap(formDataMap);

      final response = await _dio.post(
        '/api/cadastro/',
        data: formData,
        options: Options(
          contentType: 'multipart/form-data',
        ),
      );

      if (response.data is Map<String, dynamic>) {
        return Map<String, dynamic>.from(response.data);
      }

      return {
        'ok': false,
        'mensagem': 'Resposta inválida do servidor.',
        'erro': response.data.toString(),
      };
    } on DioException catch (e) {
      return {
        'ok': false,
        'mensagem': 'Erro ao sincronizar com o servidor.',
        'erro': e.response?.data?.toString() ?? e.message ?? e.toString(),
        'status_code': e.response?.statusCode,
      };
    } catch (e) {
      return {
        'ok': false,
        'mensagem': 'Erro inesperado.',
        'erro': e.toString(),
      };
    }
  }
}