import { MaterialCommunityIcons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useState } from 'react';
import { Alert, ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';

const API_URL = "https://froglike-cataleya-quirkily.ngrok-free.dev";

export default function FocusFormScreen({ navigation }) {
  const [endereco, setEndereco] = useState('');
  const [descricao, setDescricao] = useState('');
  const [tipoFoco, setTipoFoco] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!endereco || !tipoFoco) {
      Alert.alert("Aviso", "Preencha os campos obrigatórios (Endereço e Tipo do Foco).");
      return;
    }

    setLoading(true);
    try {
      const token = await AsyncStorage.getItem('session_token');
      
      const response = await fetch(`${API_URL}/api/focos/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify({
          endereco: endereco,
          descricao: descricao,
          tipo_foco: tipoFoco
        })
      });

      if (response.ok) {
        Alert.alert("Sucesso", "Foco cadastrado com sucesso!");
        navigation.goBack();
      } else {
        Alert.alert("Erro", "Não foi possível salvar o foco. Verifique os dados.");
      }
    } catch (error) {
      Alert.alert("Erro", "Erro de conexão com o servidor.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      {/* Cabeçalho */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <MaterialCommunityIcons name="arrow-left" size={24} color="#000" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Cadastrar Foco</Text>
      </View>

      <ScrollView contentContainerStyle={styles.formContainer}>
        <Text style={styles.label}>Endereço ou Localização</Text>
        <TextInput
          style={styles.input}
          placeholder="Ex: Rua Principal, 123"
          value={endereco}
          onChangeText={setEndereco}
        />

        <Text style={styles.label}>Tipo do Foco</Text>
        <TextInput
          style={styles.input}
          placeholder="Ex: Água parada, Caixa d'água"
          value={tipoFoco}
          onChangeText={setTipoFoco}
        />

        <Text style={styles.label}>Descrição / Observações</Text>
        <TextInput
          style={[styles.input, styles.textArea]}
          placeholder="Detalhes adicionais sobre o local..."
          value={descricao}
          onChangeText={setDescricao}
          multiline
          numberOfLines={4}
        />

        <TouchableOpacity style={styles.submitButton} onPress={handleSubmit} disabled={loading}>
          <Text style={styles.submitButtonText}>{loading ? "Enviando..." : "Salvar Foco"}</Text>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F5F5F5' },
  header: {
    height: 90,
    paddingTop: 35,
    paddingHorizontal: 20,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  backButton: { marginRight: 15 },
  headerTitle: { fontSize: 20, fontWeight: 'bold', color: '#000' },
  formContainer: { padding: 20 },
  label: { fontSize: 14, fontWeight: 'bold', color: '#333', marginBottom: 5, marginTop: 10 },
  input: {
    borderWidth: 1,
    borderColor: '#CCC',
    borderRadius: 8,
    height: 50,
    paddingHorizontal: 15,
    backgroundColor: '#FFF',
    color: '#000',
    marginBottom: 10,
  },
  textArea: { height: 100, textAlignVertical: 'top', paddingTop: 12 },
  submitButton: {
    backgroundColor: '#3AC0ED',
    height: 50,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 20,
  },
  submitButtonText: { color: '#000', fontWeight: 'bold', fontSize: 16 },
});